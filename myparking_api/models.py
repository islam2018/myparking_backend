from djongo import models


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

    class Meta:
        abstract = True


class Etage(models.Model):
    idEtage = models.IntegerField()
    nbPlaces = models.IntegerField()


class Paiment(models.Model):
    type = models.TextField()

    def __str__(self):
        return self.type


class Parking(models.Model):
    idParking = models.IntegerField()
    nbEtages = models.IntegerField()
    nbPlaces = models.IntegerField()
    nom = models.TextField()
    adresse = models.TextField()
    imageUrl: models.TextField()
    lattitude: models.FloatField()
    longitude: models.FloatField()
    horaire = models.EmbeddedField(model_container=Horaire)
    etages = models.ArrayReferenceField(to=Etage, on_delete=models.CASCADE, default=None)
    tarifs = models.ArrayReferenceField(to=Tarif, on_delete=models.CASCADE, default=None)
    equipements = models.ArrayReferenceField(to=Equipement, on_delete=models.CASCADE, default=None)


class Automobiliste(models.Model):
    idAutomobiliste = models.IntegerField()
    nom = models.TextField()
    prenom = models.TextField()
    mail = models.TextField()
    mdpHash = models.TextField()
    favoris = models.ArrayReferenceField(to=Parking, on_delete=models.DO_NOTHING, default=None)


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


class Evaluation(models.Model):
    idEvaluation = models.IntegerField()
    note = models.IntegerField()
    automobiliste = models.EmbeddedField(model_container=Automobiliste)
