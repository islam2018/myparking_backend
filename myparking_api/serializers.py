import json
from datetime import datetime, time

from django.contrib.auth.models import User, Permission, Group
from django.db.models import TextField
from django.utils.timezone import now
from rest_framework import serializers
from rolepermissions.roles import assign_role

from myparking import roles
from myparking.roles import Driver
from .models import Etage, Parking, Horaire, Tarif, Equipement, Automobiliste, Agent
from django.contrib.auth.hashers import make_password
import requests


class EtageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etage
        fields = ['idEtage', 'nbPlaces']
        extra_kwargs = {
            'idEtage': {'read_only': True}
        }


class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ['idHoraire', 'HeureOuverture', 'HeureFermeture']
        extra_kwargs = {
            'idHoraire': {'read_only': True}
        }


class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = ['idTarif', 'duree', 'prix']
        extra_kwargs = {
            'idTarif': {'read_only': True}
        }



class EquipementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipement
        fields = ['idEquipement', 'designation']
        extra_kwargs = {
            'idEquipement': {'read_only': True}
        }


class ParkingSerializer(serializers.ModelSerializer):
    horaire = HoraireSerializer()
    etages = EtageSerializer(many=True)
    tarifs = TarifSerializer(many=True)
    equipements = EquipementSerializer(many=True)
    ouvert = serializers.SerializerMethodField()
    routeInfo = serializers.SerializerMethodField()

    class Meta:
        model = Parking
        fields = [
            'idParking', 'nbEtages', 'nbPlaces', 'nom', 'adresse', 'imageUrl', 'lattitude', 'longitude', 'horaire',
            'etages', 'tarifs',
            'equipements', 'ouvert', 'routeInfo' ]
        extra_kwargs = {
            'idParking': {'read_only': True},
            'ouvert': {'read_only': True},
            'routeInfo': {'read_only': True}
        }


    def get_routeInfo(self,obj):
        request = self.context['request']
        try:

            start  = request.query_params['start']
            destination =   str(obj.lattitude)+","+ str(obj.longitude)
            print(start, "-->", destination)
            response = requests.get("https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json", params={
                'apiKey': 'SnEjiUueUMbL4zeFjvfi6vx4JMWGkdCrof7QDZLQWoY',
                'start0': start,
                'destination0': destination,
                'mode': 'balanced;car;traffic:enabled',
                'summaryAttributes': 'traveltime,distance'
            })
            json_data= json.loads(response.text)
            print(json_data)
            return {
                'distance': json_data['response']['matrixEntry'][0]['summary']['distance'],
                'travelTime': json_data['response']['matrixEntry'][0]['summary']['travelTime']
            }
        except Exception:
            return None


    def get_ouvert(self, obj):
        check_time =  datetime.utcnow().time()
        begin_time = obj.horaire.HeureOuverture
        end_time =  obj.horaire.HeureFermeture
        ouvert_status = False
        if begin_time < end_time:
            ouvert_status = check_time >= begin_time and check_time <= end_time
        else:  # crosses midnight
            ouvert_status = check_time >= begin_time or check_time <= end_time
        return 'Ouvert' if ouvert_status else 'Fermé'


    def create(self, validated_data):
        etages_data = validated_data.pop('etages')
        horaire_data = validated_data.pop('horaire')
        tarifs_data = validated_data.pop('tarifs')
        equipements_data = validated_data.pop('equipements')
        print(etages_data)

        etages_list = []
        tarifs_list = []
        equipements_list = []

        print(etages_data)
        for e in etages_data:
            etageModel = Etage(nbPlaces=e['nbPlaces'])
            etageModel.save()
            etages_list.append(etageModel.idEtage)
        for t in tarifs_data:
            tarifModel = Tarif( duree=t['duree'], prix=t['prix'])
            tarifModel.save()
            tarifs_list.append(tarifModel.idTarif)
        for q in equipements_data:
            equipModel = Equipement( designation=q['designation'])
            equipModel.save()
            equipements_list.append(equipModel.idEquipement)
        parking = Parking(**validated_data)
        horaire = Horaire(
            HeureOuverture=horaire_data['HeureOuverture'],
            HeureFermeture=horaire_data['HeureFermeture'])
        horaire.save()
        parking.horaire = horaire
        parking.etages_id = etages_list
        parking.tarifs_id = tarifs_list
        parking.equipements_id = equipements_list
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
        profile_data = validated_data.pop('driverProfile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        assign_role(user, roles.Driver)
        au = Automobiliste(auth=user, **profile_data)
        au.save()
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('driverProfile')
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
        user = User(username=validated_data.pop('username'), email=validated_data.pop('email'))
        user.set_password(password)
        user.save()
        assign_role(user, roles.Agent)
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

class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

