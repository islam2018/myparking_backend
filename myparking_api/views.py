from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Etage, Parking
from .serializers import EtageSerializer, ParkingSerializer


class EtageView(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer


class ParkingView(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
