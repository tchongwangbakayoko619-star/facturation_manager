import calendar
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, F, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from facturation.clients.models import Client
from facturation.invoices.models import Invoice, InvoiceLine

MONTANT_LIGNE = F("quantite") * F("prix_unitaire")


def _add_months(base_date, months):
    """Retourne base_date décalée de `months` mois (positif ou négatif)."""
    month_index = base_date.month - 1 + months
    year = base_date.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Page d'accueil : ne calcule que les statistiques simples affichées en
    haut de page (cards). Les données des graphiques sont récupérées
    séparément en JSON par le frontend (voir les vues *JSONView ci-dessous),
    pour ne pas alourdir le chargement initial de la page.
    """

    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = Invoice.objects.filter(owner=self.request.user)

        context["total_clients"] = Client.objects.filter(owner=self.request.user).count()
        context["total_invoices"] = invoices.count()
        context["invoices_paid"] = invoices.filter(status=Invoice.Status.PAID).count()
        context["invoices_overdue"] = invoices.filter(status=Invoice.Status.OVERDUE).count()
        context["recent_invoices"] = invoices.select_related("client").order_by(
            "-date_emission"
        )[:5]
        return context


class RevenueByMonthJSONView(LoginRequiredMixin, View):
    """
    Chiffre d'affaires facturé par mois, sur les 12 derniers mois.
    Basé sur la somme des lignes de facture (quantite x prix_unitaire),
    peu importe le statut de la facture (à adapter si tu veux exclure
    les factures annulées, par exemple).

    Réponse :
    {
      "labels": ["Août 2025", "Septembre 2025", ...],
      "data": [125000, 98000, ...]
    }
    """

    MONTHS_RANGE = 12

    def get(self, request):
        today = date.today()
        start_date = _add_months(date(today.year, today.month, 1), -(self.MONTHS_RANGE - 1))

        rows = (
            InvoiceLine.objects.filter(
                invoice__owner=request.user,
                invoice__date_emission__gte=start_date,
            )
            .annotate(month=TruncMonth("invoice__date_emission"))
            .values("month")
            .annotate(
                total=Coalesce(
                    Sum(MONTANT_LIGNE), 0, output_field=DecimalField(max_digits=14, decimal_places=2)
                )
            )
            .order_by("month")
        )
        totals_by_month = {row["month"]: row["total"] for row in rows}

        labels = []
        data = []
        for i in range(self.MONTHS_RANGE):
            month_date = _add_months(start_date, i)
            labels.append(f"{calendar.month_name[month_date.month]} {month_date.year}")
            data.append(float(totals_by_month.get(month_date, 0)))

        return JsonResponse({"labels": labels, "data": data})


class InvoiceStatusDistributionJSONView(LoginRequiredMixin, View):
    """
    Répartition du nombre de factures par statut.

    Réponse :
    {
      "labels": ["Brouillon", "Envoyée", "Payée", "En retard", "Annulée"],
      "data": [3, 5, 12, 2, 1]
    }
    """

    def get(self, request):
        # Comptage explicite pour garantir l'ordre et les libellés dans
        # l'ordre défini par Invoice.Status, même si un statut a 0 facture.
        from django.db.models import Count

        raw_counts = dict(
            Invoice.objects.filter(owner=request.user)
            .values_list("status")
            .annotate(count=Count("id"))
        )

        labels = [label for _, label in Invoice.Status.choices]
        data = [raw_counts.get(value, 0) for value, _ in Invoice.Status.choices]

        return JsonResponse({"labels": labels, "data": data})


class TopClientsJSONView(LoginRequiredMixin, View):
    """
    Top 5 des clients par montant total facturé (toutes factures confondues).

    Réponse :
    {
      "labels": ["Client A", "Client B", ...],
      "data": [450000, 320000, ...]
    }
    """

    LIMIT = 5

    def get(self, request):
        rows = (
            InvoiceLine.objects.filter(invoice__owner=request.user)
            .values("invoice__client__id", "invoice__client__nom")
            .annotate(
                total=Coalesce(
                    Sum(MONTANT_LIGNE), 0, output_field=DecimalField(max_digits=14, decimal_places=2)
                )
            )
            .order_by("-total")[: self.LIMIT]
        )

        labels = [row["invoice__client__nom"] for row in rows]
        data = [float(row["total"]) for row in rows]

        return JsonResponse({"labels": labels, "data": data})
