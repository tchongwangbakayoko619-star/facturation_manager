from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from facturation.clients.models import Client
from facturation.invoices.models import Invoice


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = Invoice.objects.filter(owner=self.request.user)

        context["total_clients"] = Client.objects.filter(
            owner=self.request.user,
        ).count()
        context["total_invoices"] = invoices.count()
        context["invoices_paid"] = invoices.filter(status=Invoice.Status.PAID).count()
        context["invoices_overdue"] = invoices.filter(
            status=Invoice.Status.OVERDUE,
        ).count()
        context["recent_invoices"] = invoices.select_related("client").order_by(
            "-date_emission",
        )[:5]
        return context
