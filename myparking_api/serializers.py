import json
from datetime import datetime, time

from django.contrib.auth.models import User, Permission, Group
from django.db.models import TextField
from django.utils.timezone import now
from rest_framework import serializers
from rolepermissions.roles import assign_role

from myparking import roles
from myparking.roles import Driver
from .models import Etage, Parking, Horaire, Tarif, Equipement, Automobiliste, Agent, Terme, Paiment
from django.contrib.auth.hashers import make_password
import requests


class EtageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etage
        fields = ['idEtage', 'nbPlaces']
        extra_kwargs = {
            'idEtage': {'read_only': True}
        }


class TermeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terme
        fields = ['idTerme', 'contenu']
        extra_kwargs = {
            'idTerme': {'read_only': True}
        }


class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ['idHoraire', 'jour', 'HeureOuverture', 'HeureFermeture']
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
    idEquipement = serializers.IntegerField(required=False)
    class Meta:
        model = Equipement
        fields = ['idEquipement', 'designation']
        # extra_kwargs = {
        #     'idEquipement': {'read_only': True}
        # }

class PaimentSerializer(serializers.ModelSerializer):
    idPaiment = serializers.IntegerField(required=False)
    class Meta:
        model = Paiment
        fields = ['idPaiment', 'type']


class ParkingSerializer(serializers.ModelSerializer):
    horaires = HoraireSerializer(many=True)
    etages = EtageSerializer(many=True)
    tarifs = TarifSerializer(many=True)
    equipements = EquipementSerializer(many=True)
    termes = TermeSerializer(many=True)
    paiments = PaimentSerializer(many=True)
    ouvert = serializers.SerializerMethodField()
    routeInfo = serializers.SerializerMethodField()

    class Meta:
        model = Parking
        fields = [
            'idParking', 'nbEtages', 'nbPlaces', 'nom', 'adresse', 'imageUrl', 'lattitude', 'longitude', 'horaires',
            'etages', 'tarifs', 'termes', 'paiments', 'equipements', 'ouvert', 'routeInfo']
        extra_kwargs = {
            'idParking': {'read_only': True},
            'ouvert': {'read_only': True},
            'routeInfo': {'read_only': True}
        }

    def get_routeInfo(self, obj):
        request = self.context['request']
        try:

            start = request.query_params['start']
            destination = str(obj.lattitude) + "," + str(obj.longitude)
            print(start, "-->", destination)
            response = requests.get("https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json", params={
                'apiKey': 'SnEjiUueUMbL4zeFjvfi6vx4JMWGkdCrof7QDZLQWoY',
                'start0': start,
                'destination0': destination,
                'mode': 'balanced;car;traffic:enabled',
                'summaryAttributes': 'traveltime,distance'
            })
            json_data = json.loads(response.text)
            print(json_data)
            return {
                'distance': json_data['response']['matrixEntry'][0]['summary']['distance'],
                'travelTime': json_data['response']['matrixEntry'][0]['summary']['travelTime']
            }
        except Exception:
            return None

    def get_ouvert(self, obj):
        horaires_list = list(obj.horaires_id)
        ouvert_status = False
        today = datetime.today().weekday()
        today = (today + 2) % 7
        for horaire_id in horaires_list:
            horaire = Horaire.objects.get(id=horaire_id)
            field_jour = Horaire._meta.get_field('jour')
            field_heure_ouv = Horaire._meta.get_field('HeureOuverture')
            field_heure_ferm = Horaire._meta.get_field('HeureFermeture')
            day = getattr(horaire, field_jour.attname)
            if today == day:
                check_time =  datetime.utcnow().time()
                begin_time = getattr(horaire, field_heure_ouv.attname)
                end_time =  getattr(horaire, field_heure_ferm.attname)
                if begin_time < end_time:
                    ouvert_status = check_time >= begin_time and check_time <= end_time
                else:  # crosses midnight
                    ouvert_status = check_time >= begin_time or check_time <= end_time
        return 'Ouvert' if ouvert_status else 'Fermé'


    def create(self, validated_data):
        etages_data = validated_data.pop('etages')
        horaires_data = validated_data.pop('horaires')
        tarifs_data = validated_data.pop('tarifs')
        equipements_data = validated_data.pop('equipements')
        termes_data = validated_data.pop('termes')
        paiments_data = validated_data.pop('paiments')
        print(etages_data)

        etages_list = []
        tarifs_list = []
        horaires_list = []
        termes_list = []
        equipements_list = []
        paiments_list = []

        print(etages_data)
        for h in horaires_data:
            horaireModel = Horaire(jour=h['jour'], HeureFermeture=h['HeureFermeture'],
                                   HeureOuverture=h['HeureOuverture'])
            horaireModel.save()
            horaires_list.append(horaireModel.idHoraire)
        for e in etages_data:
            etageModel = Etage(nbPlaces=e['nbPlaces'])
            etageModel.save()
            etages_list.append(etageModel.idEtage)
        for t in tarifs_data:
            tarifModel = Tarif(duree=t['duree'], prix=t['prix'])
            tarifModel.save()
            tarifs_list.append(tarifModel.idTarif)
        for q in equipements_data:
            equipModel = Equipement(designation=q['designation'])
            try:
                idEquip = q['idEquipement']
                equipModel.id = idEquip
            except Exception:
                pass
            equipModel.save()
            equipements_list.append(equipModel.idEquipement)
        for p in paiments_data:
            paimentModel = Paiment(type=p['type'])
            try:
                idPaiment = p['idPaiment']
                paimentModel.id = idPaiment
            except Exception:
                pass
            paimentModel.save()
            paiments_list.append(paimentModel.idPaiment)
        for term in termes_data:
            termModel = Terme(contenu=term['contenu'])
            termModel.save()
            termes_list.append(termModel.idTerme)
        parking = Parking(**validated_data)
        parking.horaires_id = horaires_list
        parking.etages_id = etages_list
        parking.tarifs_id = tarifs_list
        parking.termes_id = termes_list
        parking.equipements_id = equipements_list
        parking.paiments_id = paiments_list
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
