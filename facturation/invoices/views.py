import os
from collections import defaultdict
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView
from xhtml2pdf import pisa

from facturation.core.mixins import SuperuserRequiredMixin
from facturation.products.models import Product

from .forms import InvoiceForm, InvoiceLineFormSet
from .models import Invoice


def _stock_quantities_from_formset(formset):
    """Return the quantity required per product by the submitted invoice lines."""
    quantities = defaultdict(lambda: Decimal("0"))
    for line_form in formset.forms:
        data = line_form.cleaned_data
        if not data or data.get("DELETE") or not data.get("product"):
            continue
        quantities[data["product"].pk] += data["quantite"]
    return quantities


def _stock_quantities_from_invoice(invoice):
    quantities = defaultdict(lambda: Decimal("0"))
    if not invoice.pk:
        return quantities
    for line in invoice.lignes.exclude(product__isnull=True).select_related("product"):
        if line.product.gere_stock:
            quantities[line.product_id] += line.quantite
    return quantities


def reconcile_stock(invoice, formset):
    """Apply only the stock difference between the saved and submitted invoice."""
    previous = _stock_quantities_from_invoice(invoice)
    requested = _stock_quantities_from_formset(formset)
    product_ids = set(previous) | set(requested)
    products = Product.objects.select_for_update().filter(pk__in=product_ids, gere_stock=True)

    for product in products:
        change = requested[product.pk] - previous[product.pk]
        if change > 0 and (product.stock is None or product.stock < change):
            raise ValidationError(
                f"Stock insuffisant pour « {product.nom} » (disponible : {product.stock or 0})."
            )
        if change:
            product.stock = (product.stock or 0) - int(change)
            product.save(update_fields=["stock", "updated_at"])


def restore_invoice_stock(invoice):
    """Put reserved quantities back when an invoice is deleted."""
    quantities = _stock_quantities_from_invoice(invoice)
    for product in Product.objects.select_for_update().filter(pk__in=quantities, gere_stock=True):
        product.stock = (product.stock or 0) + int(quantities[product.pk])
        product.save(update_fields=["stock", "updated_at"])


def link_callback(uri, rel):
    """
    Convertit les URIs HTML statiques/médias en chemins système absolus
    pour que xhtml2pdf puisse y accéder localement sur la machine.
    """
    # Récupération des configurations statiques de Django
    s_url = settings.STATIC_URL      # Généralement '/static/'
    s_root = settings.STATIC_ROOT    # Dossier où collectstatic rassemble les fichiers
    m_url = settings.MEDIA_URL       # Généralement '/media/'
    m_root = settings.MEDIA_ROOT     # Dossier des fichiers téléversés

    # Résolution du chemin physique selon le préfixe de l'URI
    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, ""))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        # Fallback pour les chemins relatifs bruts du projet
        path = os.path.join(settings.BASE_DIR, uri)

    # Si le fichier n'existe pas, on tente de le chercher directement dans le dossier "facturation"
    if not os.path.isfile(path):
        alternative_path = os.path.join(settings.BASE_DIR, "facturation", uri.lstrip("/"))
        if os.path.isfile(alternative_path):
            path = alternative_path

    return path


def _invoice_pdf(invoice):
    """
    Generate an elegant PDF using the HTML template invoices/invoice_pdf.html
    rendered via xhtml2pdf.
    """
    context = {
        "invoice": invoice,
    }
    # Rendu du template HTML
    html_string = render_to_string("invoices/invoice_pdf.html", context)
    
    output = BytesIO()
    # Utilisation du callback pour résoudre les images locales comme le logo
    pisa_status = pisa.CreatePDF(
        src=html_string,
        dest=output,
        encoding="utf-8",
        link_callback=link_callback
    )
    
    if pisa_status.err:
        raise ValidationError(_("Erreur lors de la génération du rendu PDF."))
        
    return output.getvalue()


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    paginate_by = 15
    context_object_name = "invoices"
    template_name = "invoices/invoice_list.html"

    def get_queryset(self):
        return self._filtered_queryset()

    def _filtered_queryset(self):
        qs = Invoice.objects.filter(owner=self.request.user).select_related("client")
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        if q:
            qs = qs.filter(reference__icontains=q) | qs.filter(client__nom__icontains=q)
        if status:
            qs = qs.filter(status=status)
        return qs


class InvoiceSearchView(InvoiceListView):
    template_name = "invoices/_invoice_rows.html"


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    context_object_name = "invoice"
    template_name = "invoices/invoice_detail.html"

    def get_queryset(self):
        return Invoice.objects.filter(owner=self.request.user).prefetch_related(
            "lignes", "lignes__product"
        )


class InvoiceCreateView(LoginRequiredMixin, View):
    template_name = "invoices/invoice_form.html"

    def get(self, request):
        form = InvoiceForm(owner=request.user)
        formset = InvoiceLineFormSet(form_kwargs={"owner": request.user})
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request):
        form = InvoiceForm(request.POST, owner=request.user)
        formset = InvoiceLineFormSet(request.POST, form_kwargs={"owner": request.user})

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    invoice = form.save(commit=False)
                    invoice.owner = request.user
                    reconcile_stock(invoice, formset)
                    invoice.save()
                    formset.instance = invoice
                    formset.save()
            except ValidationError as error:
                formset._non_form_errors = formset.error_class(error.messages)
                return render(request, self.template_name, {"form": form, "formset": formset})
            messages.success(request, _("Facture créée avec succès."))
            return redirect(reverse("invoices:detail", kwargs={"pk": invoice.pk}))

        return render(request, self.template_name, {"form": form, "formset": formset})


class InvoiceUpdateView(LoginRequiredMixin, View):
    template_name = "invoices/invoice_form.html"

    def get_object(self, request, pk):
        return get_object_or_404(Invoice, pk=pk, owner=request.user)

    def get(self, request, pk):
        invoice = self.get_object(request, pk)
        form = InvoiceForm(instance=invoice, owner=request.user)
        formset = InvoiceLineFormSet(instance=invoice, form_kwargs={"owner": request.user})
        return render(
            request, self.template_name, {"form": form, "formset": formset, "invoice": invoice}
        )

    def post(self, request, pk):
        invoice = self.get_object(request, pk)
        form = InvoiceForm(request.POST, instance=invoice, owner=request.user)
        formset = InvoiceLineFormSet(
            request.POST, instance=invoice, form_kwargs={"owner": request.user}
        )

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    reconcile_stock(invoice, formset)
                    form.save()
                    formset.save()
            except ValidationError as error:
                formset._non_form_errors = formset.error_class(error.messages)
                return render(
                    request, self.template_name, {"form": form, "formset": formset, "invoice": invoice}
                )
            messages.success(request, _("Facture mise à jour."))
            return redirect(reverse("invoices:detail", kwargs={"pk": invoice.pk}))

        return render(
            request, self.template_name, {"form": form, "formset": formset, "invoice": invoice}
        )


class InvoiceLineAddView(LoginRequiredMixin, View):
    """Renvoie le HTML d'une ligne de formset vide, pour ajout dynamique (HTMX)."""

    def get(self, request):
        index = int(request.GET.get("index", 0))
        empty_form = InvoiceLineFormSet(
            instance=Invoice(), form_kwargs={"owner": request.user}
        ).empty_form
        empty_form.prefix = empty_form.prefix.replace("__prefix__", str(index))
        return render(request, "invoices/_line_row.html", {"form": empty_form})


class InvoiceDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Invoice
    template_name = "invoices/invoice_confirm_delete.html"
    success_url = reverse_lazy("invoices:list")
    context_object_name = "invoice"

    def form_valid(self, form):
        with transaction.atomic():
            restore_invoice_stock(self.object)
            response = super().form_valid(form)
        messages.success(self.request, _("Facture supprimée et stock restauré."))
        return response


class InvoicePDFView(LoginRequiredMixin, View):
    """Generate and download a PDF representation of an invoice."""

    def get(self, request, pk):
        queryset = Invoice.objects.filter(owner=request.user).select_related("client", "owner")
        invoice = get_object_or_404(queryset.prefetch_related("lignes"), pk=pk)
        response = HttpResponse(_invoice_pdf(invoice), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="facture-{invoice.reference}.pdf"'
        return response