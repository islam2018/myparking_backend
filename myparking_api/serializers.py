from rest_framework import serializers
from .models import Etage


class EtageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etage
        fields = ('idEtage', 'nbPlaces')
