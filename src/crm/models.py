from django.conf import settings
from django.db import models

# Create your models here.


class Clients(models.Model):
    """Stocke toutes les informations concernant chaque client.
    El l'absence de sales_contact, le contact est à potentiel
    et pas encore client existant"""
    first_name = models.CharField(max_length=25, verbose_name="Prénom")
    last_name = models.CharField(max_length=25, verbose_name="Nom")
    email = models.CharField(max_length=100, verbose_name="Email")
    # blank=True permt un champ faculatif, ce qui peut être le cas pour un tel fixe
    phone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True)
    mobile = models.CharField(max_length=20, verbose_name="Mobile")
    compagny_name = models.CharField(max_length=250, unique=True, verbose_name="Mobile")
    # avec auto_now_add, la date n'est actualisée qu'à la création
    date_created = models.DateTimeField(auto_now_add=True)
    # avec auto_now, la date est mise à jour à chaque modification
    date_updated = models.DateTimeField(auto_now=True)
    # pour pouvoir saisir le nom du commercial, une fois le client certain, blank=True
    sales_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                      null=True, blank=True)

    class Meta:
        ordering = ['compagny_name']
        verbose_name = "Client"

    def __str__(self):
        return self.compagny_name


class EventStatus(models.Model):
    """Défini le statut de chaque évènement"""
    status = models.CharField(max_length=25, verbose_name="Statut")

    class Meta:
        verbose_name = "Statut evènement"


class Events(models.Model):
    """Stocke toutes les informations concernant chaque évènement lié à un client """
    client = models.ForeignKey(to=Clients, on_delete=models.SET_NULL, null=True,
                               related_name='Clientevents')
    # avec auto_now_add, la date n'est actualisée qu'à la création
    date_created = models.DateTimeField(auto_now_add=True)
    # avec auto_now, la date est mise à jour à chaque modification
    date_updated = models.DateTimeField(auto_now=True)
    suport_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, related_name='Support', blank=True)
    event_status = models.ForeignKey(to=EventStatus, on_delete=models.SET_NULL, null=True, blank=True)
    attendees = models.IntegerField(blank=True, verbose_name="Participants")
    # Date quand se déroule mise à jour manuellement
    # (pour une date, si blank=True alors null=True nécessaire)
    event_date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, verbose_name="Commentaires")

    class Meta:
        verbose_name = "Evènement"


class Contracts(models.Model):
    """Stocke toutes les informations concernant chaque contrat lié à un client """
    # pour pouvoir saisir le nom du commercial, une fois le client certain, blank=True
    sales_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                      null=True, blank=True)
    client = models.ForeignKey(to=Clients, on_delete=models.SET_NULL, null=True,
                               related_name='Clientcontracts')
    event = models.OneToOneField(to=Events, on_delete=models.SET_NULL, null=True,
                                 related_name='AttachedEvent')
    # avec auto_now_add, la date n'est actualisée qu'à la création
    date_created = models.DateTimeField(auto_now_add=True)
    # avec auto_now, la date est mise à jour à chaque modification
    date_updated = models.DateTimeField(auto_now=True)
    # Statut du contrat, non signé = False, signé = True
    status = models.BooleanField(default=False, verbose_name="Signé")
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, verbose_name="Montant")
    # Date de limite de paiement
    # (pour une date, si blank=True alors null=True nécessaire)
    payment_due = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Contrat"
