import json
from rest_framework import status
from django.test import TestCase, Client
import dateutil.parser
from rest_framework.test import APIClient
from ..models import Reservation, PaiementInstance, Automobiliste
from .. import serializers
from datetime import datetime, timedelta

# initialize the APIClient app
client = APIClient()

""" Reservations tests"""
class GetReservationsTest(TestCase):
    """ Test module for GET all reservations """

    def setUp(self):
        date1 = dateutil.parser.parse("2020-02-22T20:40:00+01:00")
        date2 = dateutil.parser.parse("2020-02-22T21:40:00+01:00")
        date3 = date1 + timedelta(days=1)
        date4 = date2 + timedelta(days=1)
        paiementInstance1 = PaiementInstance.objects.create(montant="123456", date=date1)
        paiementInstance2 = PaiementInstance.objects.create(montant="654321", date=date3)
        Reservation.objects.create(automobiliste_id=1, dateEntreePrevue=date1, dateSortiePrevue=date2, parking_id=1,
                                   paiementInstance_id=paiementInstance1.idPaiementInstance, paiment_id=1)
        Reservation.objects.create(automobiliste_id=1, dateEntreePrevue=date3, dateSortiePrevue=date4, parking_id=1,
                                   paiementInstance_id=paiementInstance2.idPaiementInstance, paiment_id=1)
        self.idAutomobiliste = 1

    def test_get_reservations(self):
        response = client.get("/reservation/?" + str(self.idAutomobiliste))
        reservations = Reservation.objects.all()
        serializer = serializers.ReservationSerializer(reservations, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateReservationTest(TestCase):
    """ Test module for Reservation creation """

    def setUp(self):
        user = Automobiliste.objects.create(nom="nom_test", prenom="prenom_test", numTel="012346689",
                                            auth=json.dumps(self.user))
        client.force_authenticate(user=user)
        self.user = {
            'email': "test@test.com",
            'password': "12345abcdAB.",
            'username': "usernametest",
        }
        self.valid_payload = {
            'dateEntreePrevue': '2020-02-22T20:40:00+01:00',
            'dateSortiePrevue': '2020-02-22T21:40:00+01:00',
            'parking_id': 1,
            'automobiliste_id': 1,
            'paiment_id': 1,
            'paiementInstance': {
                'montant': '1223',
                'date': '2020-02-22T19:40:00+01:00'
            }
        }
        self.invalid_payload = {
            'dateEntreePrevue': '',
            'dateSortiePrevue': '2020-02-22T21:40:00+01:00',
            'parking_id': 1,
            'automobiliste_id': 1,
            'paiment_id': 1,
            'paiementInstance': None
        }

    def test_create_valid_reservation(self):
        response = client.post(
            '/reservation/',
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.data.parking.parking_id, 1)
        self.assertEqual(response.data.automobiliste.automobiliste_id, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_reservation(self):
        response = client.post(
            '/reservation/',
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


""" Favoris tests """


class DeleteSingleFavorisTest(TestCase):
    """ Test module for deleting an existing favoris for user  """

    def setUp(self):
        user = Automobiliste.objects.create(nom="nom_test", prenom="prenom_test", numTel="012346689",
                                            auth=json.dumps(self.user), favoris=[1, 2])
        client.force_authenticate(user=user)
        self.idAutomobiliste = 1
        self.user = {
            'email': "test@test.com",
            'password': "12345abcdAB.",
            'username': "usernametest",
        }
        self.valid_payload = {
            'favoris_id': 1
        }
        self.invalid_payload = {
            'favoris_id': 3
        }

    def test_valid_delete_modele(self):
        response = client.delete('/favoris/' + str(self.idAutomobiliste), data=json.dumps(self.valid_payload))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_modele(self):
        response = client.delete('/favoris/' + str(self.idAutomobiliste), data=json.dumps(self.invalid_payload))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
