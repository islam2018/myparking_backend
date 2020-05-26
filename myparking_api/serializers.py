import io
import json
from datetime import datetime, time
import hashlib
import random
from django.utils import timezone
import cloudinary
import cloudinary.uploader
import cloudinary.api
import qrcode
from django.contrib.auth.models import User, Permission, Group
from django.db.models import TextField
from django.http import Http404
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rolepermissions.roles import assign_role

from model_optim.persistance import setReservation
from myparking import roles
from myparking.HERE_API_KEY import HERE_API_KEY
from myparking.roles import Driver
from .models import Etage, Parking, Horaire, Tarif, Equipement, Automobiliste, Agent, Terme, Paiment, Reservation, \
    PaiementInstance, Signalement
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
        fields = ['idEquipement', 'designation', 'iconUrl']
        # extra_kwargs = {
        #     'idEquipement': {'read_only': True}
        # }

class PaimentSerializer(serializers.ModelSerializer):
    idPaiment = serializers.IntegerField(required=False)
    class Meta:
        model = Paiment
        fields = ['idPaiment', 'type', 'iconUrl']

class PaimentInstanceSerializer(serializers.ModelSerializer):
    idPaimentInstance = serializers.IntegerField(required=False)
    class Meta:
        model = PaiementInstance
        fields = ['idPaimentInstance', 'montant', 'date']



class ParkingSerializer(serializers.ModelSerializer):
    horaires = HoraireSerializer(many=True,write_only=True)
    etages = EtageSerializer(many=True)
    tarifs = TarifSerializer(many=True)
    equipements = EquipementSerializer(many=True , read_only=True)
    equipements_id = serializers.ListField(write_only=True)
    paiments = PaimentSerializer(many=True, read_only=True)
    paiments_id = serializers.ListField(write_only=True)
    termes = TermeSerializer(many=True)
    ouvert = serializers.SerializerMethodField()
    horairesStatus = serializers.SerializerMethodField()
    routeInfo = serializers.SerializerMethodField()


    class Meta:
        model = Parking
        fields = [
            'idParking', 'nbEtages', 'nbPlaces', 'nbPlacesLibres', 'nom', 'adresse', 'imageUrl', 'lattitude', 'longitude', 'horaires',
            'etages', 'tarifs', 'termes', 'paiments', 'paiments_id', 'equipements', 'equipements_id', 'horairesStatus', 'ouvert' , 'routeInfo']
        extra_kwargs = {
            'idParking': {'read_only': True},
            'ouvert': {'read_only': True},
            'routeInfo': {'read_only': True},
            'nbPlacesLibres': {'read_only': True},
            'horairesStatus': {'read_only': True},
        }



    def get_routeInfo(self, obj):
        try:
            index = (*self.instance,).index(obj)
            travelData = self.context['travelData']
            try:
                walkingData = self.context['walkingData']
                return {
                    'travelDistance': travelData[0][index],
                    'travelTime': travelData[1][index],
                    'walkingDistance': walkingData[0][index],
                    'walkingTime': walkingData[1][index],
                    'canWalk': walkingData[0][index] < 2000
                }
            except Exception:
                return None
        except Exception:
            return None



    def get_horairesStatus(self,obj):
        horaires_id_list = list(obj.horaires_id)
        horaires_list = []
        field_jour = Horaire._meta.get_field('jour')
        field_heure_ouv = Horaire._meta.get_field('HeureOuverture')
        field_heure_ferm = Horaire._meta.get_field('HeureFermeture')
        days= ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        res = []
        for horaire_id in horaires_id_list:
            horaire = Horaire.objects.get(id=horaire_id)
            horaires_list.append(horaire)
        horaires_list = sorted(horaires_list, key=lambda x: getattr(x, field_jour.attname))
        i=0
        while (i < len(horaires_list)):
            horaire = horaires_list[i]

            dayIndex = getattr(horaire, field_jour.attname)
            heure_ouv = getattr(horaire, field_heure_ouv.attname)
            heure_ferm = getattr(horaire, field_heure_ferm.attname)
            start_day = days[dayIndex-1]
            temp = []
            temp.append(start_day)
            stop = False
            j = i +1


            while (j < len(horaires_list) and stop == False):

                horaire2 = horaires_list[j]
                day2Index = getattr(horaire2, field_jour.attname)
                heure_ouv2 = getattr(horaire2, field_heure_ouv.attname)
                heure_ferm2 = getattr(horaire2, field_heure_ferm.attname)

                if (day2Index==dayIndex+1 and heure_ferm == heure_ferm2 and heure_ouv2 == heure_ouv):
                        day_desig = days[day2Index-1]
                        dayIndex = day2Index
                        temp.append(day_desig)
                        j=j+1
                else:
                    stop=True
            res.append({
                'days':temp,
                'HeureOuverture': heure_ouv,
                'HeureFermeture': heure_ferm
            })
            if (stop): i=j
            else: i=j+1
        return res



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
        equipements_list = validated_data.pop('equipements_id')
        termes_data = validated_data.pop('termes')
        paiments_list = validated_data.pop('paiments_id')

        etages_list = []
        tarifs_list = []
        horaires_list = []
        termes_list = []


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
        for term in termes_data:
            termModel = Terme(contenu=term['contenu'])
            termModel.save()
            termes_list.append(termModel.idTerme)
        parking = Parking(**validated_data)
        parking.nbPlacesLibres = validated_data['nbPlaces']
        parking.horaires_id = horaires_list
        parking.etages_id = etages_list
        parking.tarifs_id = tarifs_list
        parking.termes_id = termes_list
        parking.equipements_id = equipements_list
        parking.paiments_id = paiments_list
        parking.save()

        return parking


class AutomobilisteProfileSerializer(serializers.ModelSerializer):
    compte = serializers.CharField(required=False)
    idCompte = serializers.CharField(required=False)
    class Meta:
        model = Automobiliste
        fields = ['idAutomobiliste', 'nom', 'prenom', 'numTel', 'compte', 'idCompte']
        extra_kwargs = {'idAutomobiliste': {'read_only': True}}


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
        profile.numTel = profile_data.get('numTel', profile.numTel)

        profile.save()

        return instance

class FavorisSerializer(serializers.ModelSerializer):
    favoris = ParkingSerializer(many=True, read_only=True)
    favoris_id = serializers.ListField(write_only=True)
    class Meta:
        model = Automobiliste
        fields = ['idAutomobiliste', 'favoris', 'favoris_id']

    def to_representation(self, instance):
        fav_ids = instance.favoris_id
        parkings = ParkingSerializer(Parking.objects.filter(id__in=fav_ids),many=True,context=self.context).data
        return {
            'idAutomobiliste': instance.idAutomobiliste,
            'favoris': parkings
        }

    def create(self, validated_data):
        request = self.context['request']
        favoris_id = validated_data.pop('favoris_id')
        print(favoris_id)
        idAutomobiliste = request.query_params['automobiliste']
        driver = Automobiliste.objects.get(id=idAutomobiliste)
        for fav_id in favoris_id:
            driver.favoris_id.add(fav_id)
        driver.save()
        return driver

    def delete(self, validated_data):
        request = self.context['request']
        favoris_id = validated_data.pop('favoris_id')
        print(favoris_id)
        idAutomobiliste = request.query_params['automobiliste']
        driver = Automobiliste.objects.get(id=idAutomobiliste)
        for id in favoris_id:
            driver.favoris_id.remove(id)
        driver.save()
        return driver






class AgentProfileSerializer(serializers.ModelSerializer):
    parking = ParkingSerializer(read_only=True)
    parkingId = serializers.IntegerField(write_only=True)
    class Meta:
        model = Agent
        fields = ['idAgent', 'nom', 'prenom', 'parkingId', 'parking']
        extra_kwargs = {'idAgent': {'read_only': True}}

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
        id_parking = profile_data.pop('parkingId')
        agent = Agent(auth=user, **profile_data)
        agent.parking_id = id_parking
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
        profile.parking_id = profile_data.get('parking_id', profile.parking)
        profile.save()

        return instance


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}


class ReservationSerializer(serializers.ModelSerializer):
    parking = ParkingSerializer(read_only=True)
    automobiliste = AutomobilisteProfileSerializer(read_only=True)
    paiment = PaimentSerializer(read_only=True)
    paiment_id = serializers.IntegerField(write_only=True)
    parking_id = serializers.IntegerField(write_only=True)
    automobiliste_id = serializers.IntegerField(write_only=True)
    state = serializers.CharField(required=False)
    etageAttribue = serializers.IntegerField(required=False)
    placeAttribue = serializers.IntegerField(required=False)
    paiementInstance = PaimentInstanceSerializer()

    class Meta:
        model = Reservation
        fields = ['idReservation', 'hashId', 'codeReservation', 'qrUrl', 'state', 'etageAttribue', 'placeAttribue',
                  'dateReservation', 'dateEntreePrevue', 'dateSortiePrevue', 'dateEntreeEffective', 'dateSortieEffective',
                  'parking', 'automobiliste', 'paiment', 'paiementInstance', 'paiment_id',
                  'parking_id', 'automobiliste_id']
        extra_kwargs = {'hashId': {'read_only': True},
                        'qrUrl': {'read_only': True},
                        'codeReservation': {'read_only': True},
                        'dateReservation': {'read_only': True},
                        'dateEntreePrevue': {'required': False},
                        'dateSortiePrevue': {'required': False}}

    def create(self, validated_data):

        paiment_data = validated_data.pop('paiementInstance')
        paiment = PaiementInstance(montant=paiment_data['montant'],date=paiment_data['date'])
        paiment.save()
        dateEntree = validated_data.pop('dateEntreePrevue')
        dateSortie = validated_data.pop('dateSortiePrevue')
        x = (f"{random.randrange(99):02d}")
        y = (f"{1:02d}")
        z = y
        code = "DZ" + x + "-" + y + "-" + z
        data_to_hash = {
            "codeReservation": str(code),
            "dateEntree": str(dateEntree),
            "dateSortie":str(dateSortie),
            "idPaiement": paiment.idPaimentInstance
        }

        hashed = hashlib.md5(json.dumps(data_to_hash).encode("utf-8")).hexdigest()
        qrUrl = "" #self.generateQR(hashed)
        reservation = Reservation(paiementInstance=paiment,
                                  hashId=hashed,
                                  qrUrl = qrUrl,
                                  codeReservation=code,
                                  dateReservation=timezone.now(),
                                  dateEntreePrevue=dateEntree,
                                  dateSortiePrevue=dateSortie,
                                  dateEntreeEffective=dateEntree,
                                  dateSortieEffective=dateSortie,
                                  **validated_data)

        reservation.save()
        # Set this reservation in it's cluster
        setReservation(validated_data['automobiliste_id'],reservation)
        return reservation

    def update(self, instance, validated_data):
        reservation = instance
        reservation.dateEntreeEffective = validated_data.get('dateEntreeEffective')
        reservation.dateSortieEffective = validated_data.get('dateSortieEffective')
        instance.save()
        return instance

    def generateQR(self,content):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        b = io.BytesIO()

        img.save(b, "JPEG")
        b.seek(0)
        res = cloudinary.uploader.upload(b, folder='reservation')
        return res['url']


class SignalementSerializer(serializers.ModelSerializer):
    agent = AgentProfileSerializer()
    class Meta:
        model = Signalement
        fields = ['idSignalement','agent','type','dateDebut','dateFin','description','attachedFiles']
        extra_kwargs = {'idSignalement': {'read_only': True}}