from django.contrib import admin
from .models import Parking, Paiment, Automobiliste, Reservation, Etage, Equipement, Tarif, Evaluation

admin.site.register([Paiment, Parking, Automobiliste, Reservation, Etage, Tarif, Equipement, Evaluation])
