from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["nom", "email", "ville", "owner", "created_at"]
    list_filter = ["ville", "pays"]
    search_fields = ["nom", "email"]
    readonly_fields = ["created_at", "updated_at"]
