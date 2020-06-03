from datetime import time, datetime
from enum import Enum

from django.contrib.auth.models import User
from django.utils.timezone import now
from djongo import models
from djongo.models import DjongoManager
from django import forms
from psycopg2._psycopg import Date


class Tarif(models.Model):
    idTarif = models.AutoField(primary_key=True)
    duree = models.FloatField()
    prix = models.FloatField()

    @property
    def idTarif(self):
        return self.id


class Equipement(models.Model):
    idEquipement = models.AutoField(primary_key=True)
    designation = models.TextField()
    iconUrl = models.TextField()

    @property
    def idEquipement(self):
        return self.id


class Horaire(models.Model):
    idHoraire = models.AutoField(primary_key=True)
    jour = models.IntegerField()
    HeureOuverture = models.TimeField()
    HeureFermeture = models.TimeField()

    @property
    def idHoraire(self):
        return self.id

    objects = DjongoManager()


class Etage(models.Model):
    idEtage = models.AutoField(primary_key=True)
    nbPlaces = models.IntegerField()

    @property
    def idEtage(self):
        return self.id

    objects = DjongoManager()


class Terme(models.Model):
    idTerme = models.AutoField(primary_key=True)
    contenu = models.TextField()

    @property
    def idTerme(self):
        return self.id

    objects = DjongoManager()


class EtageForm(forms.ModelForm):
    class Meta:
        model = Etage
        fields = (
            'nbPlaces',
        )


class Paiment(models.Model):
    idPaiment = models.AutoField(primary_key=True)
    type = models.TextField()
    iconUrl = models.URLField()

    @property
    def idPaiment(self):
        return self.id

    objects = DjongoManager()


class Parking(models.Model):
    idParking = models.AutoField(primary_key=True)
    nbEtages = models.IntegerField()
    nbPlaces = models.IntegerField()
    nbPlacesLibres = models.IntegerField()
    nom = models.TextField()
    adresse = models.TextField()
    imageUrl = models.TextField()
    lattitude = models.FloatField()
    longitude = models.FloatField()
    horaires = models.ArrayReferenceField(to=Horaire, on_delete=models.CASCADE, blank=True)
    etages = models.ArrayReferenceField(to=Etage, on_delete=models.DO_NOTHING, blank=True)
    tarifs = models.ArrayReferenceField(to=Tarif, on_delete=models.DO_NOTHING, blank=True)
    equipements = models.ArrayReferenceField(to=Equipement, on_delete=models.DO_NOTHING, blank=True)
    paiments = models.ArrayReferenceField(to=Paiment, on_delete=models.DO_NOTHING, blank=True)
    termes = models.ArrayReferenceField(to=Terme, on_delete=models.DO_NOTHING, blank=True)

    @property
    def idParking(self):
        return self.id

    objects = DjongoManager()


class Automobiliste(models.Model):
    idAutomobiliste = models.AutoField(primary_key=True)
    compte = models.TextField(default='app')
    idCompte = models.TextField(default='null')
    nom = models.TextField(default='')
    numTel = models.TextField(default='')
    prenom = models.TextField(default='')
    position = models.ListField()
    auth = models.OneToOneField(to=User, on_delete=models.CASCADE, default=None, related_name='driverProfile')
    favoris = models.ArrayReferenceField(to=Parking, on_delete=models.DO_NOTHING, blank=True)
    objects = DjongoManager()

    @property
    def idAutomobiliste(self):
        return self.id


class Agent(models.Model):
    idAgent = models.AutoField(primary_key=True)
    nom = models.TextField(default='')
    prenom = models.TextField(default='')
    auth = models.OneToOneField(to=User, on_delete=models.CASCADE, default=None, related_name='agentProfile')
    parking = models.ForeignKey(to=Parking, on_delete=models.CASCADE)
    objects = DjongoManager()

    @property
    def idAgent(self):
        return self.id


class PaiementInstance(models.Model):
    idPaimentInstance = models.AutoField(primary_key=True)
    montant = models.TextField()
    date = models.DateTimeField()
    objects = DjongoManager()

    @property
    def idPaiementInstance(self):
        return self.id


class Reservation(models.Model):
    idReservation = models.AutoField(primary_key=True)
    codeReservation = models.TextField(default="")
    hashId = models.TextField()
    qrUrl = models.TextField()
    state = models.TextField(default='En cours')
    etageAttribue = models.IntegerField(default=1)
    placeAttribue = models.IntegerField(default=1)
    dateReservation = models.DateTimeField(default=datetime.today())
    dateEntreePrevue = models.DateTimeField(default=datetime.today())
    dateSortiePrevue = models.DateTimeField(default=datetime.today())
    dateEntreeEffective = models.DateTimeField(default=datetime.today())
    dateSortieEffective = models.DateTimeField(default=datetime.today())
    parking = models.ForeignKey(to=Parking, on_delete=models.CASCADE)
    automobiliste = models.ForeignKey(to=Automobiliste, on_delete=models.CASCADE)
    paiment = models.ForeignKey(to=Paiment, on_delete=models.CASCADE)
    paiementInstance = models.OneToOneField(to=PaiementInstance, on_delete=models.CASCADE, default=None)
    objects = DjongoManager()

    @property
    def idReservation(self):
        return self.id


class Evaluation(models.Model):
    idEvaluation = models.IntegerField()
    note = models.IntegerField()
    automobiliste = models.EmbeddedField(model_container=Automobiliste)

    objects = DjongoManager()

class Signalement(models.Model):
    idSignalement = models.AutoField(primary_key=True)
    agent = models.ForeignKey(to=Agent, on_delete=models.CASCADE)
    type = models.TextField()
    dateDebut = models.DateTimeField(default=now())
    dateFin = models.DateTimeField(default=now())
    description = models.TextField()
    attachedFiles = models.ListField()
    objects = DjongoManager()

    @property
    def idSignalement(self):
        return self.id

class Porposition(models.Model):
    idProposition = models.AutoField(primary_key=True)
    automobiliste = models.ForeignKey(to=Automobiliste, on_delete=models.CASCADE)
    parking = models.ForeignKey(to=Parking, on_delete=models.CASCADE)
    value = models.FloatField(default=0)

    @property
    def idProposition(self):
        return self.id


class Message(models.Model):
    idMessage = models.AutoField(primary_key=True)
    objet = models.TextField()
    message = models.TextField()
    date = models.DateTimeField(default=now())
    driver = models.ForeignKey(to=Automobiliste, on_delete=models.CASCADE)
    objects = DjongoManager()
    @property
    def idMessage(self):
        return self.id


class Cluster(models.Model):
    idCluster = models.AutoField(primary_key=True)
    label = models.TextField()
    centroid = models.ListField()
    reservations = models.ArrayReferenceField(to=Reservation, on_delete=models.CASCADE)
    parkings = models.ArrayReferenceField(to=Parking, on_delete=models.CASCADE)
    drivers = models.ArrayReferenceField(to=Automobiliste, on_delete=models.CASCADE)
    propositions = models.ArrayReferenceField(to=Porposition, on_delete=models.CASCADE)
    objects = DjongoManager()

    @property
    def idCluster(self):
        return self.id


class ETAT_RESERVATION(Enum):
    EN_COURS = "En cours"
    VALIDEE = "Validée"
    TERMINE = "Terminée"
    REFUSEE = "Refusée"
