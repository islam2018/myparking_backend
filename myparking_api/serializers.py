from rest_framework import serializers
from .models import Etage, Parking, Horaire, Tarif, Equipement


class EtageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Etage
        fields = ['idEtage', 'nbPlaces']


class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ['idHoraire', 'HeureOuverture', 'HeureFermeture']


class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = ['idTarif', 'duree', 'prix']

class EquipementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipement
        fields = ['idEquipement', 'designation']


class ParkingSerializer(serializers.ModelSerializer):
    horaire = HoraireSerializer()
    etages = EtageSerializer(many=True)
    tarifs = TarifSerializer(many=True)
    equipements = EquipementSerializer(many=True)


    class Meta:
        model = Parking
        fields = [
        'idParking', 'nbEtages', 'nbPlaces', 'nom', 'adresse', 'imageUrl', 'lattitude', 'longitude', 'horaire', 'etages','tarifs',
        'equipements',]

    def create(self, validated_data):
        etages_data = validated_data.pop('etages')
        horaire_data = validated_data.pop('horaire')
        tarifs_data = validated_data.pop('tarifs')
        equipements_data = validated_data.pop('equipements')
        print(etages_data)
        parking = Parking(**validated_data)
        etages_list = []
        tarifs_list = []
        equipements_list = []
        parking.horaire = Horaire(
            idHoraire=horaire_data['idHoraire'],
            HeureOuverture=horaire_data['HeureOuverture'],
            HeureFermeture=horaire_data['HeureFermeture'])
        for e in etages_data:
            etages_list.append(Etage(idEtage=e['idEtage'],nbPlaces=e['nbPlaces']))
        for t in tarifs_data:
            tarifs_list.append(Tarif(idTarif=t['idTarif'], duree=t['duree'], prix=t['prix']))
        for q in equipements_data:
            equipements_list.append(Equipement(idEquipement=q['idEquipement'], designation=q['designation']))
        parking.etages = etages_list
        parking.tarifs = tarifs_list
        parking.equipements = equipements_list
        parking.save()

        return parking
