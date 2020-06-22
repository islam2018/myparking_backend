""" Save and update database :
    Parking disponibility, state of clusters, users assignments
"""
import datetime
import random

import pandas as pd
from django.db import transaction
from django.utils.timezone import now
from geopy.distance import great_circle

from model_optim.helpers.calculateCentroid import get_centermost_point
from myparking_api.models import Cluster, Porposition, Reservation, Parking, ETAT_RESERVATION
import numpy as np


def saveParkingsClusters(clusters, cluster_labels, dataframe):
    # delete all old clusters first
    Cluster.objects.all().delete()
    Porposition.objects.all().delete()

    label = 0
    print("clusInPers", clusters)
    for c in clusters:
        cluster = Cluster(label=label)
        cluster.parkings_id = c['ID'].to_list()
        center = list(get_centermost_point(c[['LAT', 'LON']].to_numpy()))
        print("center")
        print("Parking ids", c['ID'].to_list())
        print(center)
        cluster.centroid = center
        cluster.save()
        # cc m3lich nroh l clusterinf? ccccccccccccccccccccc
        label = label + 1

    print(cluster_labels)
    clusters_query = Cluster.objects.all().values_list()
    clsts = pd.DataFrame.from_records(clusters_query,
                                      columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                               'drivers', 'propositions'])
    centers_ = np.asarray(clsts[['centroid']])
    for i in range(len(cluster_labels)):
        label = cluster_labels[i]
        print("label", label, i)
        if label == -1:
            crd = [dataframe.iloc[i]['LAT'], dataframe.iloc[i]['LON']]
            print(crd)
            affect = min(centers_, key=lambda point: great_circle(point, crd).m)
            result = np.where(centers_ == affect)
            idCluster = clsts.iloc[result[0][0]]['idCluster']
            c = Cluster.objects.get(id=idCluster)
            ids = list(c.parkings_id)
            print(ids, "iiddss")
            ids.append(int(dataframe.iloc[i]['ID']))
            c.parkings_id = ids
            c.save()
            pass


def saveUserAssignmentToCluster(idAutomobiliste, idCluster):
    cluster = Cluster.objects.get(id=idCluster)
    cluster.drivers_id.add(idAutomobiliste)
    reservations = Reservation.objects.filter(automobiliste_id=idAutomobiliste).values_list()
    reservations_array = np.asarray(reservations)
    if (reservations_array.__len__() > 0):
        reservations_ids = reservations_array[:, 0]
        print(reservations_ids, "iiiiids reser")
        for id in reservations_ids:
            print(id)
            cluster.reservations_id.add(id)
    cluster.save()


def saveAffectations(dataframe, users, affectations, idCluster):
    cluster = Cluster.objects.get(id=idCluster)
    array = np.asarray(affectations)
    print("array", array)
    props_id = []

    for ix, iy in np.ndindex(array.shape):

        idParking = dataframe.iloc[iy]['ID']
        idAutomobiliste = users.iloc[ix]['idAutomobiliste']
        print("prop save:")
        print(idParking, idAutomobiliste)
        # <<<<<<< HEAD
        #         if (array[ix,iy]>0):  #stupid ana
        #             proposition = Porposition(automobiliste_id=idAutomobiliste, parking_id=idParking,
        #                                       value=array[ix,iy]) # c bon, kifch nordoniwhom?
        # =======
        # haka wch ak hab dir? ma bdlt walo fel code apart 1 thing
        # wht?  whtttt
        # siyi ektb hna
        if (array[ix, iy] > 0):
            print("innn")
            proposition = Porposition(automobiliste_id=idAutomobiliste, parking_id=idParking, value=array[ix, iy])
            proposition.save()
            props_id.append(proposition.id)
    cluster.propositions_id = props_id
    cluster.save()


def setReservation(idAutomobiliste, reservation):
    cluster = Cluster.objects.get(drivers=idAutomobiliste)
    cluster.reservations_id.add(reservation.id)
    cluster.save()
    pass


def getReservations(dataframe, users, idCluster):
    cluster = Cluster.objects.get(id=idCluster)
    ids = list(cluster.reservations_id)
    print(ids, "res idsss")
    reservations = Reservation.objects.filter(id__in=ids).values_list()
    reservations_array = np.asarray(reservations)
    RESERV = []
    print(dataframe)
    print(users)
    for res in reservations_array:
        try:
            i = dataframe.loc[dataframe['ID'] == res[12]].index[0]
            j = users.loc[users['idAutomobiliste'] == res[13]].index[0]
            print(i, j, 'ij indexex parking user for reserv')
            RESERV.append({
                'i': i,
                'j': j
            })
        except Exception:
            print("GET RESERVATION FOR MODEL ERRORR")
            pass

    return RESERV


def hasReservation(idAutomobiliste):
    print("driver has reservation ?")
    reservations = Reservation.objects.filter(automobiliste_id=idAutomobiliste,
                                              state=ETAT_RESERVATION.EN_COURS.value).values_list()
    dataframe = pd.DataFrame.from_records(reservations,
                                          columns=['idReservation', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                                   '11', 'idParking', '13', '14', '15'])
    if (dataframe.size > 0):
        id_parking = dataframe.iloc[0]['idParking']
        print(id_parking)
        cluster = Cluster.objects.get(parkings=id_parking)
        print(cluster.id)
        return cluster.id
    else:
        return -1


"""FOR SIMULATION PURPOSES"""


def changeParkingDispo():
    with transaction.atomic():
        nbParkings = Parking.objects.count()
        queryset = Parking.objects.all().values_list()
        dataframe = pd.DataFrame.from_records(queryset,
                                              columns=['ID', 'NB_ETAGE', 'NB_PLACES', 'NB_PLACES_LIBRES', '4', '5', '6',
                                                       'LAT', 'LON', '9', '10', '11', '12', '13', '14'])
        ids = dataframe[['ID']]
        nbPlacesLibres = dataframe[['NB_PLACES_LIBRES']]
        print(nbParkings)

        randomCount = random.randrange(1, 100)
        print('randomCount', randomCount)

        for i in range(randomCount):
            randomStep = random.randrange(-10, 10)
            randomIndex = random.randrange(0, nbParkings - 1)
            id = ids.iloc[randomIndex]['ID']

            libre = nbPlacesLibres.iloc[randomIndex]['NB_PLACES_LIBRES']

            newLibre = libre + randomStep
            if (newLibre <= 0): newLibre = 1

            park = Parking.objects.get(id=id)
            park.nbPlacesLibres = newLibre
            park.save()
