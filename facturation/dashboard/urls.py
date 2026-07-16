from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="home"),
    path(
        "graphiques/revenus-mensuels/",
        views.RevenueByMonthJSONView.as_view(),
        name="chart_revenue_by_month",
    ),
    path(
        "graphiques/statuts-factures/",
        views.InvoiceStatusDistributionJSONView.as_view(),
        name="chart_invoice_status",
    ),
    path(
        "graphiques/top-clients/",
        views.TopClientsJSONView.as_view(),
        name="chart_top_clients",
    ),
]
