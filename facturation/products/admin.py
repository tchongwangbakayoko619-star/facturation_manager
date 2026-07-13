from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["nom", "prix_unitaire", "gere_stock", "stock", "actif", "owner"]
    list_filter = ["actif", "gere_stock"]
    search_fields = ["nom"]
    readonly_fields = ["created_at", "updated_at"]
