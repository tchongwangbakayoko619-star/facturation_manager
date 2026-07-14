from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("nouveau/", views.ProductCreateView.as_view(), name="create"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/nouvelle/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/modifier/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/supprimer/", views.CategoryDeleteView.as_view(), name="category_delete"),
    path("<int:pk>/modifier/", views.ProductUpdateView.as_view(), name="update"),
    path("<int:pk>/supprimer/", views.ProductDeleteView.as_view(), name="delete"),
    path("<int:pk>/json/", views.ProductDetailJSONView.as_view(), name="detail_json"),
]
