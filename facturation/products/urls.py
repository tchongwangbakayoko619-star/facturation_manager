from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("nouveau/", views.ProductCreateView.as_view(), name="create"),
    path("<int:pk>/modifier/", views.ProductUpdateView.as_view(), name="update"),
    path("<int:pk>/supprimer/", views.ProductDeleteView.as_view(), name="delete"),
    path("<int:pk>/json/", views.ProductDetailJSONView.as_view(), name="detail_json"),
]
