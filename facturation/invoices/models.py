import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from facturation.clients.models import Client
from facturation.products.models import Product


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        SENT = "sent", _("Envoyée")
        PAID = "paid", _("Payée")
        OVERDUE = "overdue", _("En retard")
        CANCELLED = "cancelled", _("Annulée")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("propriétaire"),
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name=_("client"),
    )
    reference = models.CharField(
        _("référence"), max_length=30, unique=True, editable=False,
    )
    date_emission = models.DateField(_("date d'émission"))
    date_echeance = models.DateField(_("date d'échéance"))
    status = models.CharField(
        _("statut"),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    notes = models.TextField(_("notes"), blank=True)
    created_at = models.DateTimeField(_("créée le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("mise à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("facture")
        verbose_name_plural = _("factures")
        ordering = ["-date_emission"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"FA-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def montant_total(self):
        return sum((ligne.montant for ligne in self.lignes.all()), 0)

    def get_absolute_url(self):
        return reverse("invoices:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.reference


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name=_("facture"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="invoice_lines",
        verbose_name=_("produit"),
        null=True,
        blank=True,
        help_text=_("Optionnel : associe cette ligne à un produit du catalogue."),
    )
    description = models.CharField(
        _("description"),
        max_length=255,
        help_text=_("Pré-rempli depuis le produit sélectionné, modifiable librement."),
    )
    quantite = models.DecimalField(
        _("quantité"), max_digits=10, decimal_places=2, default=1,
    )
    prix_unitaire = models.DecimalField(
        _("prix unitaire"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Pré-rempli depuis le produit sélectionné, modifiable librement."),
    )

    class Meta:
        verbose_name = _("ligne de facture")
        verbose_name_plural = _("lignes de facture")

    @property
    def montant(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        # Pré-remplit description/prix depuis le produit si non fournis explicitement
        if self.product_id and not self.description:
            self.description = self.product.nom
        if self.product_id and self.prix_unitaire is None:
            self.prix_unitaire = self.product.prix_unitaire
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.quantite} x {self.prix_unitaire})"
