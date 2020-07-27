import pandas as pd
from geopy.distance import great_circle

from model_optim.persistance import saveUserAssignmentToCluster, hasReservation
from myparking_api.models import Cluster, Automobiliste, Porposition
import numpy as np
from model_optim.optimization import  optimize

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
    user = Automobiliste.objects.get(id=driverId)
    old_id_cls = None
    try:
        cluster = Cluster.objects.get(drivers=driverId)
        old_id_cls = cluster.idCluster
        cluster.drivers_id.remove(driverId)
        cluster.save()
    except:
        pass
    idAutomobiliste = driverId
    clusters = Cluster.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(clusters,
                                          columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                                   'drivers', 'propositions'])

    idcls = int(hasReservation(idAutomobiliste))
    # if idcls > -1:
    #     print("existing cluster for user")
    #     print(idcls, idAutomobiliste)
    #     saveUserAssignmentToCluster(int(idAutomobiliste), int(idcls))
    #
    # else:
    ## to remove later
    if True:
        centers = np.asarray(dataframe[['centroid']])
        crd = [user.position[0], user.position[1]]
        print(crd)
        affect = min(centers, key=lambda point: great_circle(point, crd).m)
        result = np.where(centers == affect)
        idCluster = dataframe.iloc[result[0][0]]['idCluster']
        print(idCluster, idAutomobiliste)
        saveUserAssignmentToCluster(int(idAutomobiliste), int(idCluster))

        # old_props = Porposition.objects.filter(automobiliste=driverId)
        old_props = list(Porposition.objects.filter(automobiliste=3).values_list('id', flat=True))
        optimize(idCluster)
        Porposition.objects.filter(id__in=old_props).delete()

        # for cluster in dataframe.iloc:  # Run optimization on each cluster
        #     if len(cluster['parkings']) > 0 and len(cluster['drivers']) > 0:
