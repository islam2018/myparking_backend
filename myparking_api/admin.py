from django.contrib import admin
from .models import Parking, Paiment, Automobiliste, Reservation, Etage, Equipement, Tarif, Evaluation, Agent

admin.site.register([Paiment, Parking, Automobiliste, Agent, Reservation, Etage, Tarif, Equipement, Evaluation])
