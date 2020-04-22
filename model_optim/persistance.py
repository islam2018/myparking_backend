""" Save and update database :
    Parking disponibility, state of clusters, users assignments
"""
from model_optim.helpers.calculateCentroid import get_centermost_point
from myparking_api.models import Cluster, Porposition, Reservation
import numpy as np


def saveParkingsClusters(clusters):
    #delete all old clusters first
    Cluster.objects.all().delete()
    label = 0
    for c in clusters:
        cluster = Cluster(label=label)
        cluster.parkings_id = c['ID'].to_list()
        center = list(get_centermost_point(c[['LAT', 'LON']].to_numpy()))
        print(center, "center")
        cluster.centroid = center
        cluster.save()
        label = label+1

def saveUserAssignmentToCluster(idAutomobiliste, idCluster):
    cluster = Cluster.objects.get(id=idCluster)
    cluster.drivers_id.add(idAutomobiliste)
    reservations = Reservation.objects.filter(automobiliste_id=idAutomobiliste).values_list()
    reservations_array = np.asarray(reservations)
    reservations_ids = reservations_array[:,0]
    print(reservations_ids,"iiiiids reser")
    for id in reservations_ids:
        cluster.reservations_id.add(id)
    cluster.save()

def saveAffectations(dataframe, users, affectations, idCluster):
    cluster = Cluster.objects.get(id=idCluster)
    array = np.asarray(affectations)
    props_id = []
    for ix,iy in np.ndindex(array.shape):
        idParking = dataframe.iloc[iy]['ID']
        idAutomobiliste = users.iloc[ix]['idAutomobiliste']
        proposition = Porposition(automobiliste_id=idAutomobiliste, parking_id=idParking, value=array[ix,iy])
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
    for res in reservations_array:
        i = dataframe.loc[dataframe['ID'] == res[12]].index[0]
        j = users.loc[users['idAutomobiliste'] == res[13]].index[0]
        print(i,j, 'ij indexex parking user for reserv')
        RESERV.append({
            'i': i,
            'j': j
        })
    return RESERV


