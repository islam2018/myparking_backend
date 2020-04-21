import hashlib
import io
import json
import numpy as np
import cloudinary
import cloudinary.uploader
import cloudinary.api
import pandas as pd
import qrcode
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404

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
from model_optim.helpers.calculateDistance import calculateRouteInfo
from model_optim.helpers.matrixFormat import Object, splitParkings
from myparking.HERE_API_KEY import HERE_API_KEY
from myparking.roles import Driver, Agent
from .models import Etage, Parking, Automobiliste, Equipement, Reservation, Paiment
from .serializers import EtageSerializer, ParkingSerializer, AutomobilisteSerializer, AgentSerializer, AdminSerializer, \
    EquipementSerializer, ReservationSerializer, FavorisSerializer, PaimentSerializer


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
            queryParkings = getRecomendedParkings(request.query_params['automobiliste'])

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
            res = parkings


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
            parkings = ParkingSerializer(Parking.objects.all(), many=True,context={'request': request}).data
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
        return super().create(request, *args, **kwargs)

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
            data = FavorisSerializer(query).data
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
            if ((not has_role(user, IsAdminUser)) and has_role(user,Agent)):
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
