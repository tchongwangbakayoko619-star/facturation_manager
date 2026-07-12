from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def superuser_required(view_func):
    """Décorateur : combine login_required + vérification is_superuser."""

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper
