""" Save and update database :
    Parking disponibility, state of clusters, users assignments
"""
from model_optim.helpers.calculateCentroid import get_centermost_point
from myparking_api.models import Cluster
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