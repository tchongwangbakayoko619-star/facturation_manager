from django.urls import path

from . import views

app_name = "invoices"

urlpatterns = [
    path("", views.InvoiceListView.as_view(), name="list"),
    path("recherche/", views.InvoiceSearchView.as_view(), name="search"),
    path("nouvelle/", views.InvoiceCreateView.as_view(), name="create"),
    path("lignes/ajouter/", views.InvoiceLineAddView.as_view(), name="add_line"),
    path("<int:pk>/", views.InvoiceDetailView.as_view(), name="detail"),
    path("<int:pk>/pdf/", views.InvoicePDFView.as_view(), name="pdf"),
    path("<int:pk>/modifier/", views.InvoiceUpdateView.as_view(), name="update"),
    path("<int:pk>/supprimer/", views.InvoiceDeleteView.as_view(), name="delete"),
]
