import pandas as pd
from geopy.distance import great_circle

from model_optim.persistance import saveUserAssignmentToCluster
from myparking_api.models import Cluster, Automobiliste
import numpy as np

""" find a suitable cluster to the user (the closest cluster of parkings)
"""
def assignToCluster(idAutomobiliste):
    clusters = Cluster.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(clusters,
                                          columns=['idCluster', 'label', 'centroid', 'parkings', 'drivers', 'propositions'])
    centers = np.asarray(dataframe[['centroid']])
    print(centers)

    queryUser = Automobiliste.objects.filter(id=idAutomobiliste).values_list()
    user = pd.DataFrame.from_records(queryUser,
                                          columns=['idAutomobiliste', 'compte', 'idCompte', 'nom', 'numTel',
                                                   'prenom', 'position', 'auth', 'favoris']).iloc[0]

    print(user)
    crd = [user['position'][0],user['position'][1]]
    print(crd)
    affect = min(centers, key=lambda point: great_circle(point, crd).m)
    result = np.where(centers == affect)
    idCluster = dataframe.iloc[result[0][0]]['idCluster']
    print(idCluster)
    saveUserAssignmentToCluster(idAutomobiliste, idCluster)
    return idCluster

