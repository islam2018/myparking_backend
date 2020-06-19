from django.contrib import admin
from .models import Parking, Paiment, Automobiliste, Reservation, Etage, Equipement, Tarif, Evaluation, Agent, Terme, Horaire

admin.site.register([Paiment, Parking, Automobiliste, Agent, Reservation, Etage, Tarif, Equipement, Terme, Horaire])
