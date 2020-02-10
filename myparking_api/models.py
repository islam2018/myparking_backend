from django.contrib.auth.models import User
from djongo import models
from djongo.models import DjongoManager


class Tarif(models.Model):
    idTarif = models.IntegerField()
    duree = models.FloatField()
    prix = models.FloatField()


class Equipement(models.Model):
    idEquipement = models.IntegerField()
    designation = models.TextField()


class Horaire(models.Model):
    idHoraire = models.IntegerField()
    HeureOuverture = models.TimeField()
    HeureFermeture = models.TimeField()

    objects = DjongoManager()



class Etage(models.Model):
    idEtage = models.IntegerField()
    nbPlaces = models.IntegerField()

    objects = DjongoManager()


class Paiment(models.Model):
    type = models.TextField()

    objects = DjongoManager()
    def __str__(self):
        return self.type


class Parking(models.Model):
    idParking = models.IntegerField()
    nbEtages = models.IntegerField()
    nbPlaces = models.IntegerField()
    nom = models.TextField()
    adresse = models.TextField()
    imageUrl= models.TextField()
    lattitude= models.FloatField()
    longitude= models.FloatField()
    horaire = models.EmbeddedField(model_container=Horaire)
    etages = models.ArrayField(model_container=Etage)
    tarifs = models.ArrayField(model_container=Tarif)
    equipements = models.ArrayField(model_container=Equipement)

    objects = DjongoManager()

class Automobiliste(models.Model):
    idAutomobiliste = models.IntegerField()
    nom = models.TextField( default='')
    prenom = models.TextField( default='')
    auth = models.OneToOneField(to=User, on_delete=models.CASCADE, default=None, related_name='profile')
    favoris = models.ArrayReferenceField(to=Parking, on_delete=models.DO_NOTHING, blank=True)
    objects = DjongoManager()


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
