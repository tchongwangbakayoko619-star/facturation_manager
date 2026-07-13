from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    nom = models.CharField(_("Nom"), max_length=100)
    email = models.EmailField(_("Email"), max_length=254, blank=True, default='')
    telephone = models.CharField(_("Téléphone"), max_length=20, blank=True, default='')
    adresse = models.TextField(_("Adresse"), blank=True, default='')  # Ajouter default=''
    ville = models.CharField(_("Ville"), max_length=100, blank=True, default='')  # Ajouter default=''
    code_postal = models.CharField(_("Code postal"), max_length=20, blank=True, default='')  # Ajouter default=''
    pays = models.CharField(_("Pays"), max_length=50, blank=True, default="France")
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='clients', 
        verbose_name=_("Propriétaire")
    )
    
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de modification"), auto_now=True)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('clients:detail', kwargs={'pk': self.pk})