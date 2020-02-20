import math

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
from rest_framework_simplejwt.views import TokenObtainPairView
from rolepermissions.checkers import has_role


from myparking.roles import Driver, Agent
from .models import Etage, Parking, Automobiliste, Equipement, Reservation
from .serializers import EtageSerializer, ParkingSerializer, AutomobilisteSerializer, AgentSerializer, AdminSerializer, \
    EquipementSerializer, ReservationSerializer


class EtageView(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer


class ParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    permission_classes = []
    authentication_classes = []


    def filterParkings(self, request):
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
        try:
            parkings = ParkingSerializer(Parking.objects.all(), many=True, context={'request': request}).data
            res = filter(lambda parking:self.applyFilter(parking,{
                'minDistance':int(minDistance),
                'maxDistance':int(maxDistance),
                'minPrice':int(minPrice),
                'maxPrice':int(maxPrice),
                'equipements_id':equipements_id
                }),parkings)
        except Parking.DoesNotExist:
            raise Http404

        return Response(res)

    def applyFilter(self,parking, filters):
        distance = int(parking['routeInfo']['distance'])
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
            minDistance = parkings[0]['routeInfo']['distance']
            maxDistance = 0
            minPrice = parkings[0]['tarifs'][0]['prix']
            maxPrice = 0
            for parking in parkings:
                distance = parking['routeInfo']['distance']
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
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except Exception:
            return Response({
                "detail": "Creating Reservation Transaction Error"
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class DriverLoginViewJWT(TokenObtainPairView):
    user_serializer_class = AutomobilisteSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = get_user_model().objects.get(username=request.data[get_user_model().USERNAME_FIELD])
            if ((not has_role(user, IsAdminUser)) and has_role(user,Driver)):
                serialized_user = self.user_serializer_class(user)
                response.data.update(serialized_user.data)
            else:
                response = Response({
                    'detail': 'You are not allowed to perform this action'
                }, status.HTTP_403_FORBIDDEN)
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
