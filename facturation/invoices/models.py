import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from facturation.clients.models import Client


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
        _("référence"),
        max_length=30,
        unique=True,
        editable=False,
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

    def get_absolute_url(self):
        return reverse("invoices:detail", kwargs={"pk": self.pk})

    @property
    def montant_total(self):
        return sum((ligne.montant for ligne in self.lignes.all()), 0)

    def __str__(self):
        return self.reference


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name=_("facture"),
    )
    description = models.CharField(_("description"), max_length=255)
    quantite = models.DecimalField(
        _("quantité"),
        max_digits=10,
        decimal_places=2,
        default=1,
    )
    prix_unitaire = models.DecimalField(
        _("prix unitaire"),
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        verbose_name = _("ligne de facture")
        verbose_name_plural = _("lignes de facture")

    @property
    def montant(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.description} ({self.quantite} x {self.prix_unitaire})"
