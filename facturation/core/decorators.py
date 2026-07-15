from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def superuser_required(view_func):
    """
    Décorateur pour vues-fonctions : combine login_required + vérification is_superuser.

    - Non connecté -> redirection vers la page de login.
    - Connecté mais pas superuser -> 403 (PermissionDenied).
    - Superuser -> exécution normale de la vue.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return login_required(wrapper)