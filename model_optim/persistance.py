""" Save and update database :
    Parking disponibility, state of clusters, users assignments
"""
from model_optim.helpers.calculateCentroid import get_centermost_point
from myparking_api.models import Cluster, Porposition
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


""" COMPLETE THIS LATER TO ADD RESERVATION CONTRAINT IN MODEL"""
def getReservations(dataframe,users,idCluster):
    return []


