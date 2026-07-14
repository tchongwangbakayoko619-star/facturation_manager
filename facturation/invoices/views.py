from collections import defaultdict
from decimal import Decimal
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView

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


def _pdf_text(value):
    """Escape a string for the small, dependency-free PDF renderer."""
    text = str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("latin-1", "replace").decode("latin-1")


def _invoice_pdf(invoice):
    """Create a basic PDF invoice without requiring a system PDF binary."""
    lines = [
        f"FACTURE {invoice.reference}",
        f"Client : {invoice.client}",
        f"Date d'emission : {invoice.date_emission}    Echeance : {invoice.date_echeance}",
        f"Statut : {invoice.get_status_display()}",
        "",
        "Description                              Qte       Prix        Montant",
        "-" * 78,
    ]
    for line in invoice.lignes.all():
        description = str(line.description)[:38]
        lines.append(
            f"{description:<40} {line.quantite:>6}  {line.prix_unitaire:>10}  {line.montant:>10}"
        )
    lines.extend(["-" * 78, f"TOTAL : {invoice.montant_total}"])
    if invoice.notes:
        lines.extend(["", "Notes :", str(invoice.notes)])

    commands = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index:
            commands.append("T*")
        commands.append(f"({_pdf_text(line)}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = BytesIO()
    output.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode())
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_offset = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode())
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010} 00000 n \n".encode())
    output.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )
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
