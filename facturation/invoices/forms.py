from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

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
            ),
            "date_echeance": forms.DateInput(
                attrs={"type": "date", "class": INPUT_CLASS},
            ),
            "status": forms.Select(attrs={"class": INPUT_CLASS}),
            "notes": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
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
            raise forms.ValidationError(
                {
                    "date_echeance": _(
                        "La date d'échéance ne peut pas être antérieure "
                        "à la date d'émission.",
                    ),
                },
            )

        return cleaned_data


class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ["description", "quantite", "prix_unitaire"]
        widgets = {
            "description": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "quantite": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "step": "0.01", "min": "0"},
            ),
            "prix_unitaire": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "step": "0.01", "min": "0"},
            ),
        }


InvoiceLineFormSet = inlineformset_factory(
    Invoice,
    InvoiceLine,
    form=InvoiceLineForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
