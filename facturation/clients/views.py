from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from facturation.core.mixins import OwnerRequiredMixin

from .forms import ClientForm
from .models import Client


class ClientListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Client
    paginate_by = 15
    context_object_name = "clients"
    template_name = "clients/client_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nom__icontains=q)
        return qs


class ClientDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Client
    context_object_name = "client"
    template_name = "clients/client_detail.html"


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, _("Client créé avec succès."))
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        messages.success(self.request, _("Client mis à jour."))
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Client
    template_name = "clients/client_confirm_delete.html"
    success_url = reverse_lazy("clients:list")
    superuser_bypass = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Client supprimé."))
        return response
