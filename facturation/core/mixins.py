from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Combine la vérification de connexion (redirige vers allauth login si non connecté)
    et la vérification is_superuser (403 si connecté mais pas autorisé).
    """

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied


class OwnerRequiredMixin:
    """
    Restreint un queryset aux objets appartenant à l'utilisateur connecté.
    Le modèle doit avoir un champ `owner` pointant vers AUTH_USER_MODEL.
    """

    owner_field = "owner"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.owner_field: self.request.user})
