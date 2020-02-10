from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Etage, Parking, Automobiliste
from .serializers import EtageSerializer, ParkingSerializer, UserSerializer


class EtageView(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer


class ParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer


class RegistrationView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []
    serializer_class = UserSerializer


class UserLoginViewJWT(TokenObtainPairView):
    user_serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = get_user_model().objects.get(username=request.data[get_user_model().USERNAME_FIELD])
            serialized_user = self.user_serializer_class(user)
            response.data.update(serialized_user.data)
        return response
