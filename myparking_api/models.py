from django.contrib.auth.models import User
from djongo import models
from djongo.models import DjongoManager
from django import forms


class Tarif(models.Model):
    idTarif =  models.AutoField(primary_key=True)
    duree = models.FloatField()
    prix = models.FloatField()

    @property
    def idTarif(self):
        return self.id


class Equipement(models.Model):
    idEquipement =  models.AutoField(primary_key=True)
    designation = models.TextField()
    iconUrl = models.TextField()

    @property
    def idEquipement(self):
        return self.id


class Horaire(models.Model):
    idHoraire  = models.AutoField(primary_key=True)
    jour = models.IntegerField()
    HeureOuverture = models.TimeField()
    HeureFermeture = models.TimeField()

    @property
    def idHoraire(self):
        return self.id

    objects = DjongoManager()


class Etage(models.Model):
    idEtage =  models.AutoField(primary_key=True)
    nbPlaces = models.IntegerField()

    @property
    def idEtage(self):
        return self.id

    objects = DjongoManager()

class Terme(models.Model):
    idTerme =  models.AutoField(primary_key=True)
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
    prenom = models.TextField(default='')
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
    parking = models.TextField()
    objects = DjongoManager()

    @property
    def idAgent(self):
        return self.id


class Reservation(models.Model):
    idReservation = models.IntegerField()
    date = models.DateField()
    entreePrevue = models.DateField(default='something')
    sortiePrevue = models.DateField()
    entreeEffective = models.DateField()
    sortieEffective = models.DateField()
    parking = models.OneToOneField(Parking, on_delete=models.CASCADE, default='something')
    automobiliste = models.OneToOneField(Automobiliste, on_delete=models.CASCADE)
    paiement = models.OneToOneField(Paiment, on_delete=models.CASCADE)

    objects = DjongoManager()


class Evaluation(models.Model):
    idEvaluation = models.IntegerField()
    note = models.IntegerField()
    automobiliste = models.EmbeddedField(model_container=Automobiliste)

    objects = DjongoManager()
