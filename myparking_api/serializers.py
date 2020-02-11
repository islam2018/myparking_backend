from django.contrib.auth.models import User, Permission, Group
from django.db.models import TextField
from rest_framework import serializers
from .models import Etage, Parking, Horaire, Tarif, Equipement, Automobiliste, Agent
from django.contrib.auth.hashers import make_password


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
            'idParking', 'nbEtages', 'nbPlaces', 'nom', 'adresse', 'imageUrl', 'lattitude', 'longitude', 'horaire',
            'etages', 'tarifs',
            'equipements', ]

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
            etages_list.append(Etage(idEtage=e['idEtage'], nbPlaces=e['nbPlaces']))
        for t in tarifs_data:
            tarifs_list.append(Tarif(idTarif=t['idTarif'], duree=t['duree'], prix=t['prix']))
        for q in equipements_data:
            equipements_list.append(Equipement(idEquipement=q['idEquipement'], designation=q['designation']))
        parking.etages = etages_list
        parking.tarifs = tarifs_list
        parking.equipements = equipements_list
        parking.save()

        return parking


class AutomobilisteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automobiliste
        fields = ['idAutomobiliste', 'nom', 'prenom']


class AutomobilisteSerializer(serializers.HyperlinkedModelSerializer):
    driverProfile = AutomobilisteProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'driverProfile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        au = Automobiliste(auth=user, **profile_data)
        au.save()
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.idAutomobiliste = profile_data.get('idAutomobiliste', profile.idAutomobiliste)
        profile.nom = profile_data.get('nom', profile.nom)
        profile.prenom = profile_data.get('prenom', profile.prenom)

        profile.save()

        return instance


class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['idAgent', 'nom', 'prenom', 'parking']


class AgentSerializer(serializers.HyperlinkedModelSerializer):
    agentProfile = AgentProfileSerializer(required=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'agentProfile']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        profile_data = validated_data.pop('agentProfile')
        password = validated_data.pop('password')
        user = User(username=validated_data.pop('username'),email=validated_data.pop('email'))
        user.set_password(password)
        user.save()
        agent = Agent(auth=user, **profile_data)
        agent.save()
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('agentProfile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.idAutomobiliste = profile_data.get('idAgent', profile.idAutomobiliste)
        profile.nom = profile_data.get('nom', profile.nom)
        profile.prenom = profile_data.get('prenom', profile.prenom)
        profile.parking = profile_data.get('parking', profile.parking)
        profile.save()

        return instance
