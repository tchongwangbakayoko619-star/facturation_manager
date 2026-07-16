from django import forms

from .models import Category
from .models import Product

INPUT_CLASS = (
    "w-full border border-gray-300 rounded-lg px-3 py-2 "
    "focus:ring-2 focus:ring-indigo-500 focus:outline-none"
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "nom",
            "category",
            "description",
            "image",
            "prix_unitaire",
            "gere_stock",
            "stock",
            "actif",
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "category": forms.Select(attrs={"class": INPUT_CLASS}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "block w-full text-sm text-gray-600 "
                        "file:mr-4 file:py-2 file:px-4 "
                        "file:rounded-lg file:border-0 "
                        "file:bg-indigo-50 file:text-indigo-700 "
                        "hover:file:bg-indigo-100"
                    ),
                },
            ),
            "prix_unitaire": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "step": "0.01", "min": "0"},
            ),
            "stock": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": "0"}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields["category"].queryset = Category.objects.filter(owner=owner)

    def clean(self):
        cleaned_data = super().clean()
        gere_stock = cleaned_data.get("gere_stock")
        stock = cleaned_data.get("stock")
        if gere_stock and stock is None:
            self.add_error(
                "stock",
                "Indique une quantité de stock si le suivi de stock est activé.",
            )
        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size") and image.size > 5 * 1024 * 1024:
            msg = "L'image ne doit pas dépasser 5 Mo."
            raise forms.ValidationError(msg)
        return image


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["nom", "description"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
        }
