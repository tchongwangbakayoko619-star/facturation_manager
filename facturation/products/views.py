from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from facturation.core.mixins import OwnerRequiredMixin, SuperuserRequiredMixin

from .forms import CategoryForm
from .forms import ProductForm
from .models import Category
from .models import Product


class ProductListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Product
    paginate_by = 15
    context_object_name = "products"
    template_name = "products/product_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nom__icontains=q) | qs.filter(category__nom__icontains=q)
        return qs


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, _("Produit créé avec succès."))
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class ProductUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        messages.success(self.request, _("Produit mis à jour."))
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class ProductDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        messages.success(self.request, _("Produit supprimé."))
        return super().form_valid(form)


class ProductDetailJSONView(LoginRequiredMixin, View):
    """
    Renvoie description + prix_unitaire d'un produit en JSON.
    Appelé en JS/HTMX quand l'utilisateur sélectionne un produit
    dans une ligne de facture, pour auto-remplir les champs.
    """

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, owner=request.user)
        return JsonResponse(
            {
                "description": product.nom,
                "prix_unitaire": str(product.prix_unitaire),
                "en_rupture": product.en_rupture,
            }
        )


class CategoryListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Category
    context_object_name = "categories"
    template_name = "products/category_list.html"
    paginate_by = 15


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy("products:category_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, _("Catégorie créée avec succès."))
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy("products:category_list")

    def form_valid(self, form):
        messages.success(self.request, _("Catégorie mise à jour."))
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Category
    template_name = "products/category_confirm_delete.html"
    success_url = reverse_lazy("products:category_list")
    context_object_name = "category"

    def form_valid(self, form):
        messages.success(self.request, _("Catégorie supprimée."))
        return super().form_valid(form)
