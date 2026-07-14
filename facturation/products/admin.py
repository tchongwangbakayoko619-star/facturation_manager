from django.contrib import admin

from .models import Category
from .models import Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["nom", "owner", "created_at"]
    search_fields = ["nom"]
    list_filter = ["owner"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["nom", "category", "prix_unitaire", "gere_stock", "stock", "actif", "owner"]
    list_filter = ["actif", "gere_stock", "category"]
    search_fields = ["nom", "category__nom"]
    readonly_fields = ["created_at", "updated_at"]
