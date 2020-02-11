from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rolepermissions.checkers import has_role

from myparking.permissions import IsAgent, IsDriver
from myparking.roles import Driver, Agent
from .models import Etage, Parking, Automobiliste
from .serializers import EtageSerializer, ParkingSerializer, AutomobilisteSerializer, AgentSerializer


class EtageView(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer


class ParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    def get_permissions(self):
        permission_classes = []
        print("***********************",has_role(self.request.user,Agent))
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        elif self.action == 'retrieve' :
            permission_classes = [IsAgent]
        elif self.action == 'list' :
            permission_classes = [IsDriver]
        return [permission() for permission in permission_classes]


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
            serialized_user = self.user_serializer_class(user)
            response.data.update(serialized_user.data)
        return response


class AgentLoginViewJWT(TokenObtainPairView):
    user_serializer_class = AgentSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = get_user_model().objects.get(username=request.data[get_user_model().USERNAME_FIELD])
            serialized_user = self.user_serializer_class(user)
            response.data.update(serialized_user.data)
        return response
