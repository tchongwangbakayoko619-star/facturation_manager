from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_image_upload_path(instance, filename):
    return f"products/{instance.owner_id}/{filename}"


class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("propriétaire"),
    )
    nom = models.CharField(_("nom"), max_length=150)
    description = models.TextField(_("description"), blank=True)
    image = models.ImageField(
        _("image"),
        upload_to=product_image_upload_path,
        blank=True,
        null=True,
        help_text=_("Format recommandé : carré, 800x800px maximum."),
    )
    prix_unitaire = models.DecimalField(_("prix unitaire"), max_digits=12, decimal_places=2)
    gere_stock = models.BooleanField(
        _("gérer le stock"),
        default=False,
        help_text=_("Active le suivi de quantité disponible pour ce produit."),
    )
    stock = models.PositiveIntegerField(_("stock disponible"), null=True, blank=True)
    actif = models.BooleanField(_("actif"), default=True, help_text=_("Visible dans les listes de sélection."))
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("produit")
        verbose_name_plural = _("produits")
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse("products:update", kwargs={"pk": self.pk})

    @property
    def en_rupture(self):
        return self.gere_stock and self.stock is not None and self.stock <= 0
