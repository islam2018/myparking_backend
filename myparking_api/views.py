from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rolepermissions.checkers import has_role

from myparking.permissions import IsAgent, IsDriver
from myparking.roles import Driver, Agent
from .models import Etage, Parking, Automobiliste
from .serializers import EtageSerializer, ParkingSerializer, AutomobilisteSerializer, AgentSerializer, AdminSerializer


class EtageView(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer


class ParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    permission_classes = []
    authentication_classes = []

    def getOneParking(self, request, idParking=None):
        parking = get_object_or_404(self.queryset, id=idParking)
        serializer = ParkingSerializer(parking, context={'request': request})
        return Response(serializer.data)


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
