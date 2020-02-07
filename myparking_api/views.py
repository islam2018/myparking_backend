from django.shortcuts import render
from rest_framework import viewsets
from .models import Etage
from .serializers import EtageSerializer


class EtageView(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer
