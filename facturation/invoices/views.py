from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView

from facturation.core.mixins import SuperuserRequiredMixin

from .forms import InvoiceForm, InvoiceLineFormSet
from .models import Invoice


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
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.owner = request.user
                invoice.save()
                formset.instance = invoice
                formset.save()
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
            with transaction.atomic():
                form.save()
                formset.save()
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
        messages.success(self.request, _("Facture supprimée."))
        return super().form_valid(form)
