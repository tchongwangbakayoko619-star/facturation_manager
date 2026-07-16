from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import FieldDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
""" les mixins"""

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
    Le modèle doit avoir un champ (ou lookup) pointant vers AUTH_USER_MODEL.
    """

    owner_field: str = "owner"
    superuser_bypass: bool = False

    def get_owner_field(self) -> str:
        return self.owner_field

    def get_queryset(self):
        qs = super().get_queryset()

        user = self.request.user

        # Défense en profondeur : même si LoginRequiredMixin protège la vue,
        # on ne fait jamais confiance implicitement à un user anonyme.
        if not user.is_authenticated:
            return qs.none()

        if self.superuser_bypass and user.is_superuser:
            return qs

        field_name = self.get_owner_field()

        # Valide que le champ existe réellement sur le modèle, pour échouer
        # explicitement (erreur de config) plutôt que de renvoyer un queryset
        # vide silencieusement en cas de faute de frappe dans owner_field.
        model = qs.model
        try:
            # Utilisation de get_field() qui est une méthode publique de Options
            model._meta.get_field(field_name.split("__")[0])  # noqa: SLF001
        except FieldDoesNotExist as exc:
            msg = (
                f"{self.__class__.__name__}: le champ '{field_name}' "
                f"n'existe pas sur le modèle {model.__name__}."
            )
            raise ImproperlyConfigured(msg) from exc

        return qs.filter(**{field_name: user})
