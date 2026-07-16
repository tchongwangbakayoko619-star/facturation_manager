from django import forms
from django.forms import inlineformset_factory

from facturation.products.models import Product

from .models import Invoice
from .models import InvoiceLine

INPUT_CLASS = (
    "w-full border border-gray-300 rounded-lg px-3 py-2 "
    "focus:ring-2 focus:ring-indigo-500 focus:outline-none"
)


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["client", "date_emission", "date_echeance", "status", "notes"]
        widgets = {
            "client": forms.Select(attrs={"class": INPUT_CLASS}),
            "date_emission": forms.DateInput(
                attrs={"type": "date", "class": INPUT_CLASS},
                format="%Y-%m-%d",
            ),
            "date_echeance": forms.DateInput(
                attrs={"type": "date", "class": INPUT_CLASS},
                format="%Y-%m-%d",
            ),
            "status": forms.Select(attrs={"class": INPUT_CLASS}),
            "notes": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Force le format ISO (YYYY-MM-DD) en plus du format du widget :
        # <input type="date"> exige ce format pour afficher la valeur, et le
        # navigateur envoie aussi ce format au POST. Sans ça, la locale fr
        # (jj/mm/aaaa) casse l'affichage ET peut casser la validation.
        self.fields["date_emission"].input_formats = ["%Y-%m-%d"]
        self.fields["date_echeance"].input_formats = ["%Y-%m-%d"]

        if owner is not None:
            client_field = self.fields["client"]
            client_field.queryset = client_field.queryset.model.objects.filter(
                owner=owner,
            )

    def clean(self):
        cleaned_data = super().clean()
        date_emission = cleaned_data.get("date_emission")
        date_echeance = cleaned_data.get("date_echeance")
        if date_emission and date_echeance and date_echeance < date_emission:
            msg = "La date d'échéance ne peut pas être antérieure à la date d'émission."
            raise forms.ValidationError(
                msg,
            )
        return cleaned_data


class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ["product", "description", "quantite", "prix_unitaire"]
        widgets = {
            # data-product-select est utilisé par le JS pour détecter les changements
            # et appeler l'endpoint JSON products:detail_json (auto-remplissage)
            "product": forms.Select(
                attrs={"class": INPUT_CLASS, "data-product-select": "true"},
            ),
            "description": forms.TextInput(
                attrs={"class": INPUT_CLASS, "data-line-description": "true"},
            ),
            "quantite": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "step": "0.01", "min": "0"},
            ),
            "prix_unitaire": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASS,
                    "step": "0.01",
                    "min": "0",
                    "data-line-price": "true",
                },
            ),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        product_field = self.fields["product"]
        product_field.required = False
        product_field.empty_label = "— Aucun produit (saisie libre) —"

        qs = Product.objects.filter(actif=True)
        if owner is not None:
            qs = qs.filter(owner=owner)

        # Si la ligne existante référence un produit désormais inactif (ou
        # exclu par le filtre owner), on le réinjecte dans le queryset pour
        # qu'il reste sélectionné à l'affichage au lieu d'apparaître vide.
        current_product_id = (
            self.instance.product_id if self.instance and self.instance.pk else None
        )
        if current_product_id and not qs.filter(pk=current_product_id).exists():
            qs = qs | Product.objects.filter(pk=current_product_id)

        product_field.queryset = qs

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantite = cleaned_data.get("quantite")
        if product and product.gere_stock and quantite is not None:
            if quantite <= 0:
                self.add_error("quantite", "La quantité doit être supérieure à zéro.")
            elif quantite != quantite.to_integral_value():
                self.add_error(
                    "quantite",
                    "Un produit géré en stock doit avoir une quantité entière.",
                )
        return cleaned_data


InvoiceLineFormSet = inlineformset_factory(
    Invoice,
    InvoiceLine,
    form=InvoiceLineForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
