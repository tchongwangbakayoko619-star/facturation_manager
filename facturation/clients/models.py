from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name=_("propriétaire"),
    )
    nom = models.CharField(_("nom"), max_length=150)
    email = models.EmailField(_("email"), blank=True)
    telephone = models.CharField(_("téléphone"), max_length=30, blank=True)
    adresse = models.TextField(_("adresse"), blank=True)
    ville = models.CharField(_("ville"), max_length=100, blank=True)
    pays = models.CharField(_("pays"), max_length=100, blank=True)
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse("clients:update", kwargs={"pk": self.pk})
