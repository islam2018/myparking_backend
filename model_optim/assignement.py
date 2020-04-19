import pandas as pd
from geopy.distance import great_circle

from model_optim.persistance import saveUserAssignmentToCluster
from myparking_api.models import  Cluster
import numpy as np

""" find a suitable cluster to the user (the closest cluster of parkings)
"""
def assignToCluster(idAutomobiliste, lat, lon):
    clusters = Cluster.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(clusters,
                                          columns=['idCluster', 'label', 'centroid', 'parkings', 'drivers', 'propositions'])
    centers = np.asarray(dataframe[['centroid']])
    print(centers)

    crd = [lat,lon]
    affect = min(centers, key=lambda point: great_circle(point, crd).m)
    result = np.where(centers == affect)
    idCluster = dataframe.iloc[result[0][0]]['idCluster']
    print(idCluster)
    saveUserAssignmentToCluster(idAutomobiliste, idCluster)
    return idCluster

