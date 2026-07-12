from django.contrib import admin

from .models import Invoice
from .models import InvoiceLine


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "client",
        "status",
        "date_emission",
        "date_echeance",
        "montant_total",
    ]
    list_filter = ["status", "date_emission"]
    search_fields = ["reference", "client__nom"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    inlines = [InvoiceLineInline]

    def montant_total(self, obj):
        return obj.montant_total

    montant_total.short_description = "Montant total"
