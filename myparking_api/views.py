import base64
import binascii
import hashlib
import hmac
import io
import json
import numpy as np
import cloudinary
import cloudinary.uploader
import cloudinary.api
import pandas as pd
import qrcode
from datetime import datetime as dt, timedelta, datetime
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.timezone import now

from rest_framework import viewsets, permissions, status, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rolepermissions.checkers import has_role

from model_optim.affectation import getRecomendedParkings
from model_optim.forSimulationOnly import getTestRecommandations
from model_optim.helpers.calculateDistance import calculateRouteInfo
from model_optim.helpers.matrixFormat import Object, splitParkings
from model_optim.simulation import main_test_fun
from myparking import roles, beams_agent_client, beams_driver_client
from myparking.HERE_API_KEY import HERE_API_KEY
from myparking.roles import Driver
from .models import Etage, Parking, Automobiliste, Equipement, Reservation, Paiment, Agent, ETAT_RESERVATION, \
    Signalement, Message
from .serializers import EtageSerializer, ParkingSerializer, AutomobilisteSerializer, AgentSerializer, AdminSerializer, \
    EquipementSerializer, ReservationSerializer, FavorisSerializer, PaimentSerializer, AgentProfileSerializer, \
    SignalementSerializer, MessageSerializer
from pusher_push_notifications import PushNotifications

class EquipementView(viewsets.ModelViewSet):
    queryset = Equipement.objects.all()
    serializer_class = EquipementSerializer
    permission_classes = []
    authentication_classes = []

class PaiementView(viewsets.ModelViewSet):
    queryset = Paiment.objects.all()
    serializer_class = PaimentSerializer
    permission_classes = []
    authentication_classes = []


class ParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    permission_classes = []
    authentication_classes = []


    def list(self, request, *args, **kwargs):
        try:
            (queryParkings,ids,weights) = getRecomendedParkings(request.query_params['automobiliste'])

            try:
                start = request.query_params['start']
            except Exception:
                start = None
            try:
                destination = request.query_params['destination']
            except Exception:
                destination = None

            (travelData, walkingData) = calculateRouteInfo(queryParkings, start, destination)

            parkings = ParkingSerializer(queryParkings, many=True, context={
                'request': request, 'walkingData': walkingData,
                'travelData': travelData}).data
            res = parkings.sort(key=lambda p: weights[ids.index(p['idParking'])]) # c bon sah? hhhoui truni? att k



        except Parking.DoesNotExist:
            raise Http404


        try:
            minDistance = request.query_params['minDistance']
        except Exception:
            minDistance = 0
        try:
            maxDistance = request.query_params['maxDistance']
        except Exception:
            maxDistance = 1000000000
        try:
            minPrice = request.query_params['minPrice']
        except Exception:
            minPrice = 0
        try:
            maxPrice = request.query_params['maxPrice']
        except Exception:
            maxPrice = 1000000000
        try:
            equipements_id = request.query_params['equipements'].split(',')
        except Exception:
            equipements_id = []
        print(minDistance,maxDistance, minPrice, maxPrice,equipements_id)
        if(minDistance != 0 or maxDistance!=1000000000 and minPrice!=0 or maxPrice!=0 or equipements_id!=[]):
            res = filter(lambda parking: self.applyFilter(parking, {
                'minDistance': int(minDistance),
                'maxDistance': int(maxDistance),
                'minPrice': int(minPrice),
                'maxPrice': int(maxPrice),
                'equipements_id': equipements_id
            }), parkings)
        return Response(res)



    def applyFilter(self,parking, filters):
        try:
            distance = int(parking['routeInfo']['walkingDistance'])
            minPrice = filters['minPrice']
            maxPrice = filters['maxPrice']
            equipements = filters['equipements_id']
            hasPrice = False
            if filters['minDistance'] <= distance <= filters['maxDistance']:
                for tarif in parking['tarifs']:
                    price=int(tarif['prix'])
                    if minPrice <= price <= maxPrice:
                        hasPrice = True
                if hasPrice:
                    hasAllEquip = True
                    for equip in equipements:
                        hasEquip=False
                        for equipPark in parking['equipements']:
                            if int(equipPark['idEquipement'])==int(equip):
                                hasEquip=True
                        if (hasEquip==False):
                            hasAllEquip=False
                    if hasAllEquip:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        except Exception:
            return True



    # def getOneParking(self, request, idParking=None):
    #     parking = get_object_or_404(self.queryset, id=idParking)
    #     serializer = ParkingSerializer(parking, context={'request': request})
    #     return Response(serializer.data)


    # def get_permissions(self):
    #     permission_classes = []
    #     print("***********************",has_role(self.request.user,Agent))
    #     if self.action == 'create' or self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
    #         permission_classes = [IsAdminUser]
    #     elif self.action == 'retrieve' :
    #         permission_classes = [IsAgent]
    #     elif self.action == 'list' :
    #         permission_classes = [IsDriver]
    #     return [permission() for permission in permission_classes]

class FilterInfosView(mixins.ListModelMixin,GenericViewSet):
    queryset = Equipement.objects.all()
    serializer_class = EquipementSerializer
    permission_classes = []
    authentication_classes = []
    def list(self, request, *args, **kwargs):
        try:
            equipements = EquipementSerializer(self.queryset, many=True).data
        except Equipement.DoesNotExist:
            raise Http404
        try:
            try:
                start = request.query_params['start']
            except Exception:
                start = None
            try:
                destination = request.query_params['destination']
            except Exception:
                destination = None

            queryParkings = getRecomendedParkings(request.query_params['automobiliste'])
            (travelData, walkingData) = calculateRouteInfo(queryParkings, start, destination)
            parkings = ParkingSerializer(queryParkings, many=True, context={
                'request': request, 'walkingData': walkingData,
                'travelData': travelData}).data
            minDistance = parkings[0]['routeInfo']['walkingDistance']
            maxDistance = 0
            minPrice = parkings[0]['tarifs'][0]['prix']
            maxPrice = 0
            for parking in parkings:
                distance = parking['routeInfo']['walkingDistance']
                if (distance <= minDistance):
                    minDistance = distance
                if (distance >= maxDistance):
                    maxDistance = distance
                for tarif in parking['tarifs']:
                    price = tarif['prix']
                    if (price <= minPrice):
                        minPrice = price
                    if (price >= maxPrice):
                        maxPrice = price

        except Parking.DoesNotExist:
            raise Http404
        return Response({
            'equipements': equipements,
            'prix': {
                'min': minPrice,
                'max': maxPrice
            },
            'distance': {
                'min': minDistance,
                'max': maxDistance
            }
        })

class ReservationView(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    permission_classes = []
    authentication_classes = []
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        # try:
        #     with transaction.atomic():
        #         return super().create(request, *args, **kwargs)
        # except Exception:
        #     return Response({
        #         "detail": "Creating Reservation Transaction Error"
        #     }, status.HTTP_500_INTERNAL_SERVER_ERROR)
        # with transaction.atomic():
        #     return super().create(request, *args, **kwargs)

        with transaction.atomic():
            response = super().create(request, *args, **kwargs).data
            content_ = {
                "0": response['idReservation'],
                "1": response['dateReservation'],
                "2": response['dateEntreePrevue'],
                "3": response['dateSortiePrevue'],
                "4": response['parking']['idParking'],
                "5": response['automobiliste']['nom']+";"+response['automobiliste']['prenom'],
            }
            content = json.dumps(content_, cls=DjangoJSONEncoder)
            content_bytes = content.encode('ascii')
            #base64_bytes = base64.b64encode(content_bytes)
            # content_bytes = content.encode('utf-8')
            base64_message = binascii.hexlify(content_bytes)

            print(base64_message)
            print(content)
            qrUrl = self.serializer_class().generateQR(content)
            reservation = Reservation.objects.get(id=response['idReservation'])
            reservation.qrUrl = qrUrl
            reservation.save()
            return Response(ReservationSerializer(reservation, many=False).data)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)
        except Exception:
            return Response({
                "detail": "Creating Reservation Transaction Error"
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            automobiliste_id = request.query_params['automobiliste_id']
            query = Reservation.objects.filter(automobiliste_id=automobiliste_id)
            data = ReservationSerializer(query,many=True,context={'request': request}).data
            return Response(data)
        except Exception:
            print("catched exception")
            return super().list(request, *args, **kwargs)

    def checkQR(self,request, code):
        try:
            reservation = Reservation.objects.get(hashId=code)
            data = ReservationSerializer(reservation, many=False).data
            return Response(data)
        except Http404:
            return Response({
                'detail': 'Reservation non trouvée'
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                'detail': 'Internal server error'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def validateQR(self, request,id):
        try:
            reservation = Reservation.objects.get(id=id)
            if reservation.state == ETAT_RESERVATION.EN_COURS.value:
                reservation.state = ETAT_RESERVATION.VALIDEE.value
                reservation.dateEntreeEffective = datetime.now()
            elif reservation.state == ETAT_RESERVATION.VALIDEE.value:
                reservation.state = ETAT_RESERVATION.TERMINE.value
                reservation.dateSortieEffective = datetime.now()
            elif reservation.state == ETAT_RESERVATION.TERMINE.value:
                return Response({
                    "detail": "Réservation déja validé"
                }, status.HTTP_409_CONFLICT)
            elif reservation.state == ETAT_RESERVATION.REFUSEE.value:
                return Response({
                    "detail": "Réservation déja refusée"
                }, status.HTTP_409_CONFLICT)
            reservation.save()
            return Response(ReservationSerializer(reservation,many=False).data)
        except Http404:
            return Response({
                "detail": "Réservation non trouvée"
            }, status.HTTP_404_NOT_FOUND)

    def declineQR(self, request,id):
        try:
            reservation = Reservation.objects.get(id=id)
            if reservation.state == ETAT_RESERVATION.EN_COURS.value:
                reservation.state = ETAT_RESERVATION.REFUSEE.value
            elif reservation.state == ETAT_RESERVATION.VALIDEE.value or reservation.state == ETAT_RESERVATION.TERMINE.value:
                return Response({
                    "detail": "Réservation déja validé"
                }, status.HTTP_409_CONFLICT)
            elif reservation.state == ETAT_RESERVATION.REFUSEE.value:
                return Response({
                    "detail": "Réservation déja refusée"
                }, status.HTTP_409_CONFLICT)
            reservation.save()
            return Response(ReservationSerializer(reservation, many=False).data)
        except Http404:
            return Response({
                "detail": "Réservation non trouvée"
            }, status.HTTP_404_NOT_FOUND)

    def history(self,request):
        try:
            id_parking = request.query_params['parking']
            date = dt.strptime(request.query_params['date'], '%d-%m-%Y')
            end_date = date + timedelta(days=1)
            print(date, end_date)
            valideStates = [ETAT_RESERVATION.VALIDEE.value, ETAT_RESERVATION.TERMINE.value]
            nbReservations = Reservation.objects.filter(parking_id=id_parking,
                                                        dateReservation__range=(date, end_date)).count()
            nbReservationsValidee = Reservation.objects.filter(parking_id=id_parking,
                                                        state__in=valideStates,
                                                        dateReservation__range=(date, end_date)).count()
            nbReservationsRefusee = Reservation.objects.filter(parking_id=id_parking,
                                                               state=ETAT_RESERVATION.REFUSEE.value,
                                                               dateReservation__range=(date, end_date)).count()
            return Response({
                "date": date,
                "nbReservationsTotal": nbReservations,
                "nbReservationsValidee": nbReservationsValidee,
                "nbReservationsRefusee": nbReservationsRefusee
            })
        except Exception:
            return Response({
                'detail': 'Internal server error'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegistrationAutomobilisteView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []
    serializer_class = AutomobilisteSerializer


class RegistrationAgentView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []
    serializer_class = AgentSerializer

class FavorisView(viewsets.ModelViewSet):
    queryset = Automobiliste.objects.all()
    permission_classes = []
    authentication_classes = []
    serializer_class = FavorisSerializer

    def list(self, request, *args, **kwargs):
        try:
            idAutomobiliste = request.query_params['automobiliste']
            query = Automobiliste.objects.get(id=idAutomobiliste)
            fav_ids = list(query.favoris_id)
            print(fav_ids)
            queryParkings = Parking.objects.filter(id__in=fav_ids)
            try:
                start = request.query_params['start']
            except Exception:
                start = None
            try:
                destination = request.query_params['destination']
            except Exception:
                destination = None

            (travelData, walkingData) = calculateRouteInfo(queryParkings, start, destination)
            data = FavorisSerializer(query, context={
                'request': request, 'walkingData': walkingData,
                'travelData': travelData}).data
            return Response(data)
        except Http404:
            return Response({
                'detail': 'Automobiliste non existant'
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                'detail': 'Internal server error'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            idAutomobiliste = request.query_params['automobiliste']
            query = Automobiliste.objects.get(id=idAutomobiliste)
            serializer = FavorisSerializer(query,context={'request': request})
            serializer.delete(request.data)
            return Response(serializer.data)
        except Http404:
            return Response({
                'detail': 'Automobiliste non existant'
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                'detail': 'Internal server error'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DriverLoginViewJWT(TokenObtainPairView):
    user_serializer_class = AutomobilisteSerializer

    def post(self, request, *args, **kwargs):
        try:
            fromFacebook = request.data.pop('fromFb')
            fbId = request.data['driverProfile']['idCompte']
        except Exception:
            fromFacebook = False
            fbId=0
        if not fromFacebook:
            response = super().post(request, *args, **kwargs)
            user = get_user_model().objects.get(username=request.data[get_user_model().USERNAME_FIELD])
        else:
            try:
                driver = Automobiliste.objects.get(idCompte=fbId, compte='facebook')
                user = driver.auth
            except Exception:
                data = request.data
                data['password'] = hashlib.md5(fbId.encode("utf-8")).hexdigest()
                user = AutomobilisteSerializer().create(data)
            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status.HTTP_200_OK)

        if response.status_code == status.HTTP_200_OK:
            if ((not has_role(user, IsAdminUser)) and has_role(user, Driver)):
                serialized_user = self.user_serializer_class(user)
                response.data.update(serialized_user.data)
            else:
                response = Response({
                    'detail': 'You are not allowed to perform this action'
                }, status.HTTP_403_FORBIDDEN)
            return response
        return response







class AgentLoginViewJWT(TokenObtainPairView):
    user_serializer_class = AgentSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = get_user_model().objects.get(username=request.data[get_user_model().USERNAME_FIELD])
            if ((not has_role(user, IsAdminUser)) and has_role(user,roles.Agent)):
                serialized_user = self.user_serializer_class(user)
                response.data.update(serialized_user.data)
            else:
                response = Response({
                    'detail': 'You are not allowed to perform this action'
                }, status.HTTP_403_FORBIDDEN)

        return response

class AdminLoginViewJWT(TokenObtainPairView):
    user_serializer_class = AdminSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = get_user_model().objects.get(username=request.data[get_user_model().USERNAME_FIELD])
            if (not has_role(user, IsAdminUser)):
                response = Response({
                    'detail': 'You are not allowed to perform this action'
                }, status.HTTP_403_FORBIDDEN)
            else:
                serialized_user = self.user_serializer_class(user)
                response.data.update(serialized_user.data)
        return response

class SearchView(APIView):
    #permission_classes = [IsDriver]
    def get(self, request):
        query = None
        try:
            query =  request.query_params['query']
        except Exception:
            return Response({
                "detail": "Bad request parameters"
            }, status.HTTP_400_BAD_REQUEST)
        try:
            if query:
                url = "https://places.sit.ls.hereapi.com/places/v1/autosuggest"
                headers = {'Accept': 'application/json'}
                params = {
                    'apiKey': HERE_API_KEY,
                    'in': '36.0998,3.2953;r=300000',
                    'q': query
                }
                response = requests.get(url,params,headers=headers)
                return Response(json.loads(response.text))
            else:
                return Response({
                    "detail": "Request error"
                }, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            return Response({
                "detail": "Request error"
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentView(APIView):
    # permission_classes = [IsDriver]
    def get(self, request, id):
        agent = Agent.objects.get(id=id)
        agent_data = AgentProfileSerializer(agent, many=False).data
        id_parking = agent.parking_id
        parking = Parking.objects.get(id=id_parking)
        date = dt.strptime(request.query_params['date'], '%d-%m-%Y')
        end_date = date + timedelta(days=1)
        print(date, end_date)
        nbReservations = Reservation.objects.filter(parking_id=id_parking,dateReservation__range=(date,end_date)).count()

        return Response(
            {
                'date': date,
                'idParking': id_parking,
                'nbReservations': nbReservations,
                'nbPlaces': parking.nbPlaces,
                'nbPlacesLibres': parking.nbPlacesLibres,
                'nbPlacesOccupes': parking.nbPlaces - parking.nbPlacesLibres,
            }
        )

class SignalementView(viewsets.ModelViewSet):
    permission_classes = []
    authentication_classes = []
    def create(self, request, *args, **kwargs):

        data = json.loads(request.data['body'])
        date_debut = datetime.strptime(data["date_debut"], '%d-%m-%Y %H:%M')
        date_fin = datetime.strptime(data["date_fin"], '%d-%m-%Y %H:%M')
        idAgent = data["agent"]
        type = data["type"]
        description = data["description"]
        links =[]
        for f in self.request.FILES.getlist('file'):
             res = cloudinary.uploader.upload(f, folder='attached', resource_type='raw')
             links.append(res['url'])
        signalement = Signalement(description=description,dateDebut=date_debut,dateFin=date_fin,type=type,attachedFiles=links)
        signalement.agent_id = idAgent
        signalement.save()
        result = SignalementSerializer(signalement,many=False).data
        return Response(result)
        pass


class BeamsAgentAuth(APIView):
    def get(self, request):
        id = request.query_params['user_id']
        beams_token = beams_agent_client.generate_token("agent"+id)
        return Response(beams_token)
class BeamsDriverAuth(APIView):
    def get(self, request):
        id = request.query_params['user_id']
        beams_token = beams_driver_client.generate_token("driver"+id)
        return Response(beams_token)



class SendAgentNotif(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self,request):
        title = request.data['title']
        message = request.data['body']
        content = request.data['content']
        user_id = request.data['user_id']
        aav= "agent"+user_id  ## fix this LATER
        response = beams_agent_client.publish_to_users(
            user_ids=[aav],
            publish_body={

                'fcm': {
                    # 'notification': {
                    #     'title': title,
                    #     'body': message,
                    # },
                    'data': {
                        'title': title,
                        'body': message,
                        'content': content
                    }
                },

            }
        )
        return Response(response)

class BroadcastAgent(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self,request):
        title = request.data['title']
        message = request.data['body']
        content = request.data['content']
        interest = request.data['interest']
        response = beams_agent_client.publish_to_interests(
            interests=[interest],
            publish_body={

                'fcm': {
                    # 'notification': {
                    #     'title': title,
                    #     'body': message
                    # },
                    'data': {
                        'title': title,
                        'body': message,
                        'content': content
                    }
                },

            }
        )
        return Response(response)

class SendDriverNotif(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self,request):
        title = request.data['title']
        message = request.data['body']
        content = request.data['content']
        user_id = request.data['user_id']
        aav= "driver"+user_id  ## fix this LATER
        response = beams_driver_client.publish_to_users(
            user_ids=[aav],
            publish_body={

                'fcm': {
                    # 'notification': {
                    #     'title': title,
                    #     'body': message,
                    # },
                    'data': {
                        'title': title,
                        'body': message,
                        'content': content
                    }
                },

            }
        )
        return Response(response)

class BroadcastDriver(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self,request):
        title = request.data['title']
        message = request.data['body']
        content = request.data['content']
        interest = request.data['interest']
        response = beams_driver_client.publish_to_interests(
            interests=[interest],
            publish_body={

                'fcm': {
                    # 'notification': {
                    #     'title': title,
                    #     'body': message
                    # },
                    'data': {
                        'title': title,
                        'body': message,
                        'content': content
                    }
                },

            }
        )
        return Response(response)

class UpdateLocation(viewsets.ModelViewSet):
    permission_classes = []
    authentication_classes = []
    def updateDriverLocation(self, request):
        driverId = request.data['driverId']
        lat = request.data['lat']
        long = request.data['long']
        au = Automobiliste.objects.get(id=driverId)
        au.position=[lat,long]
        au.save()
        return Response("Position mis à jour.")


class ContactView(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = []
    authentication_classes = []


class TestParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    permission_classes = []
    authentication_classes = []
    def withMode(self, request, *args, **kwargs):
        try:
            mode = int(request.query_params['mode'])
            print(mode)
            #hadi the view ndjibo recommadntaions,
            #if mode=0 il utilise l'objet propositons(f la bdd)
            #if mode1 il utilise variable globale fiha (300*100) maderthach f bdd psk pour les tests berk
            #if mod=2 yraj2 ga3 les arpkings
            (queryParkings,ids,weights) =getTestRecommandations(int(request.query_params['automobiliste']),int(mode))
            #apres ma yradj2 il filtredjat error wrili le bulk machin plz hhhh no mechi update li prbo look
            #asebri rani nwerilek
            try:
                start = request.query_params['start']
            except Exception:
                start = None
            try:
                destination = request.query_params['destination']
            except Exception:
                destination = None
            #(travelData, walkingData) = calculateRouteInfo(queryParkings, start, destination)
            # hadi 9otlek dertha en comment bech mayehsbch routeIfo
            parkings = ParkingSerializer(queryParkings, many=True, context={
                'request': request, }).data
            # copy it melhih wher e?
            if(mode<2):
                res = parkings.sort(key=lambda p: weights[ids.index(p['idParking'])]) # c bon sah? hhhoui truni? att k
            else:
                res = parkings

        except Parking.DoesNotExist:
            raise Http404
        # hna il filtre pour min , max ,etx fhamti ,? les filtres fdhmt , mzlha mkltni start and destination kichghol ma rahmch used
        # f our tests, sah rana we update them later, but comme each user rah ydir one request ma kch fyada nn?
        # mefhatmch bsah m bekri kona using berk his positino, psk amdakhlnahc destiantion fl modele
        # ahhhh sah? oui 9olna ndakhloha mais ma3refnach (koa mazel ma kheana bien), mais f clustring it's using his positon, li rahi
        #f la bdd and it's updated a, mala lzm w uodate la bdd b the random positions kbl ma nruniw request
        #raki dayertha ani dyrtha kbel?o
        try:
            minDistance = request.query_params['minDistance']
        except Exception:
            minDistance = 0
        try:
            maxDistance = request.query_params['maxDistance']
        except Exception:
            maxDistance = 1000000000
        try:
            minPrice = request.query_params['minPrice']
        except Exception:
            minPrice = 0
        try:
            maxPrice = request.query_params['maxPrice']
        except Exception:
            maxPrice = 1000000000
        try:
            equipements_id = request.query_params['equipements'].split(',')
        except Exception:
            equipements_id = []
        print(minDistance, maxDistance, minPrice, maxPrice, equipements_id)
        if (minDistance != 0 or maxDistance != 1000000000 and minPrice != 0 or maxPrice != 0 or equipements_id != []):
            res = filter(lambda parking: self.applyFilter(parking, {
                'minDistance': int(float(minDistance)),
                'maxDistance': int(float(maxDistance)),
                'minPrice': int(float(minPrice)),
                'maxPrice': int(float(maxPrice)),
                'equipements_id': equipements_id
            }), parkings)
        return Response(res)

    def applyFilter(self,parking, filters):
        try:
            distance = int(parking['routeInfo']['walkingDistance'])
            minPrice = filters['minPrice']
            maxPrice = filters['maxPrice']
            equipements = filters['equipements_id']
            hasPrice = False
            if filters['minDistance'] <= distance <= filters['maxDistance']:
                for tarif in parking['tarifs']:
                    price=int(tarif['prix'])
                    if minPrice <= price <= maxPrice:
                        hasPrice = True
                if hasPrice:
                    hasAllEquip = True
                    for equip in equipements:
                        hasEquip=False
                        for equipPark in parking['equipements']:
                            if int(equipPark['idEquipement'])==int(equip):
                                hasEquip=True
                        if (hasEquip==False):
                            hasAllEquip=False
                    if hasAllEquip:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        except Exception:
            return True

    def ruTests(self):
        main_test_fun()
        return Response("Model ran")