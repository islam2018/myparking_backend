import os
import random

import hdbscan
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances
import pandas as pd
import numpy as np
from optimisation_model.util_functions import distanceMatrixForClustering, get_centermost_point, parkingsInRadius
import seaborn as sns
import matplotlib.pyplot as plt

plot_kwds = {'alpha': 0.5, 's': 80, 'linewidths': 0}


def initParkingClusters():
    dataframe = pd.DataFrame(list(Parking.objects.all()[10:].values()))  # all parkings dataframe
    min_samples = dataframe[
        'nbPlaces'].mean().__int__()  # places libre in a parking to be considered core point and custer random.randrange(5, row['nbPlaces']
    dataframe['nbPlacesDisponibles'] = dataframe.apply(lambda row: row['nbPlaces'] // 2,
                                                       axis=1)  # can be fetched from real source later
    center = get_centermost_point(dataframe[['lattitude', 'longitude']].to_numpy())
    # print("center", center)
    # filteredDf = parkingsInRadius(dataframe, center)
    filteredDf = dataframe.copy()
    matrix_distance = distanceMatrixForClustering(filteredDf, min_samples)
    # print("minsam", min_samples)
    earth_radius_km = 6371.0088
    epsilon = 3 / earth_radius_km
    # db = DBSCAN(eps=3,
    #             min_samples=min_samples,
    #             algorithm='auto',
    #             metric='precomputed',
    #             ).fit(matrix_distance, y=None, sample_weight=dataframe['nbPlacesDisponibles'].to_numpy())
    clusterer = hdbscan.HDBSCAN(
        metric='precomputed',
        min_cluster_size=5,
        min_samples=4,
    )

    db = clusterer.fit(matrix_distance)
    cluster_labels = db.labels_
    # soft_clusters = hdbscan.all_points_membership_vectors(clusterer)
    # print("soft clusters", soft_clusters)

    num_clusters = len(set(cluster_labels))
    # plot purposes
    # coordinates = filteredDf[['lattitude', 'longitude']].to_numpy()
    # palette = sns.color_palette('Paired', np.unique(cluster_labels).max() + 1)
    # colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in cluster_labels]
    # plt.scatter(coordinates[:, 0], coordinates[:, 1], c=colors, **plot_kwds)
    #
    # plt.show()
    clusters = pd.Series([filteredDf[cluster_labels == n] for n in range(-1, num_clusters - 1)])
    return clusters


# after this use each cluster to create a seperate model and inject new users
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, OptimizationCluster

    parking_zones = initParkingClusters()
    for index, c in enumerate(parking_zones):
        liste = c['id'].to_list()
        cluster = OptimizationCluster(parkings_id=[*liste])
        cluster.save()
    # total = 0
    # for index, c in enumerate(parking_zones):
    #     print('Cluster {} : {} places libres, head : {}'.format(index, c['nbPlacesDisponibles'].sum(), c.shape))
    #     total += c.shape[0]
    # print('total of clustered parkings', total)
    # print('Number  of  clusters: {}'.format(parking_zones.shape[0]))

    # colors_centers = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in range(cluster_labels.max() + 1)]
