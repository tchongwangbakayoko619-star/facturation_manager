from django import forms

from .models import Client

INPUT_CLASS = (
    "w-full border border-gray-300 rounded-lg px-3 py-2 "
    "focus:ring-2 focus:ring-indigo-500 focus:outline-none"
)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["nom", "email", "telephone", "adresse", "ville", "pays"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_CLASS}),
            "telephone": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "adresse": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
            "ville": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "pays": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }
