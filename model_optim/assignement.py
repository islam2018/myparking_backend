import pandas as pd
from geopy.distance import great_circle

from model_optim.persistance import saveUserAssignmentToCluster, hasReservation
from myparking_api.models import Cluster, Automobiliste
import numpy as np

""" find a suitable cluster to the user (the closest cluster of parkings)
"""
def assignToClusters():
    queryUsers = Automobiliste.objects.all().values_list()
    users = pd.DataFrame.from_records(queryUsers,
                                      columns=['idAutomobiliste', 'compte', 'idCompte', 'nom', 'numTel',
                                               'prenom', 'position', 'auth', 'favoris'])

    clusters = Cluster.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(clusters,
                                          columns=['idCluster', 'label', 'centroid','reservations', 'parkings', 'drivers', 'propositions'])
    centers = np.asarray(dataframe[['centroid']])
    print(centers)
    print("centers")
    for user in users.iloc:
        print(user)
        idAutomobiliste = user['idAutomobiliste']
        idcls = int(hasReservation(idAutomobiliste))
        if idcls > -1:
            print(idcls, idAutomobiliste)
            saveUserAssignmentToCluster(int(idAutomobiliste), int(idcls))
        else:
            crd = [user['position'][0],user['position'][1]]
            print(crd)
            affect = min(centers, key=lambda point: great_circle(point, crd).m)
            result = np.where(centers == affect)
            idCluster = dataframe.iloc[result[0][0]]['idCluster']
            print(idCluster, idAutomobiliste)
            saveUserAssignmentToCluster(int(idAutomobiliste), int(idCluster))

def updateClusterAssignement(driverId):
    queryUsers = Automobiliste.objects.filter(id=driverId).values_list()
    user = pd.DataFrame.from_records(queryUsers,
                                      columns=['idAutomobiliste', 'compte', 'idCompte', 'nom', 'numTel',
                                               'prenom', 'position', 'auth', 'favoris'])
    try:
        cluster = Cluster.objects.get(drivers=driverId)
        cluster.drivers.remove(driverId)
        cluster.save()
    except:
        pass
    idAutomobiliste = driverId
    clusters = Cluster.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(clusters,
                                          columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                                   'drivers', 'propositions'])
    centers = np.asarray(dataframe[['centroid']])
    idcls = int(hasReservation(idAutomobiliste))
    if idcls > -1:
        print(idcls, idAutomobiliste)
        saveUserAssignmentToCluster(int(idAutomobiliste), int(idcls))
    else:
        crd = [user['position'][0], user['position'][1]]
        print(crd)
        affect = min(centers, key=lambda point: great_circle(point, crd).m)
        result = np.where(centers == affect)
        idCluster = dataframe.iloc[result[0][0]]['idCluster']
        print(idCluster, idAutomobiliste)
        saveUserAssignmentToCluster(int(idAutomobiliste), int(idCluster))
