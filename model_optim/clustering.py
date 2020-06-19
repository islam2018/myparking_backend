import seaborn as sns
import pandas as pd
from django.db import transaction
from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt

from model_optim.assignement import assignToClusters
from model_optim.helpers.calculateDistance import calculateDistance
from model_optim.optimization import optimize
from model_optim.persistance import saveParkingsClusters
from myparking_api.models import Parking, Automobiliste, Cluster

""" Generate clusters of parkings : 
    using DBSCAN to cluster parkings in database
"""

def getParkingClusters():
    queryset = Parking.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(queryset,columns=['ID','NB_ETAGE','NB_PLACES','NB_PLACES_LIBRES','4','5','6','LAT','LON','9','10','11','12','13','14'])
    # print(dataframe)
    # hna bdlt nb place b nb places klibres
    min_samples = dataframe['NB_PLACES_LIBRES'].mean().__int__()
    matrix_distance = calculateDistance(dataframe, min_samples)
    earth_radius_km = 6371.0088
    epsilon = 1 / earth_radius_km
    crd = dataframe[['LAT', 'LON']].to_numpy()
    data = crd

    db = DBSCAN(eps=1,
                min_samples=min_samples,
                algorithm='auto',
                metric='precomputed',
                ).fit(matrix_distance, y=None,
                      sample_weight=dataframe['NB_PLACES_LIBRES'].to_numpy())
    cluster_labels = db.labels_
    print("clusttterr", cluster_labels)
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([dataframe[cluster_labels == n] for n in range(num_clusters)])

    palette = sns.color_palette('deep', np.unique(cluster_labels).max() + 1)
    plot_kwds = {'alpha': 0.5, 's': 80, 'linewidths': 0}
    c_colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in cluster_labels]

    plt.scatter(crd[:, 0], crd[:, 1], c=c_colors, **plot_kwds)

    # plt.show()

    saveParkingsClusters(clusters, cluster_labels, dataframe)  # Save into database

    return (cluster_labels, clusters,crd)


#getParkingClusters()
#assignToCluster(1)
#optimize(2)
#getRecomendedParkings(2)

# with transaction.atomic():
#     getParkingClusters()  # Clusetring and save into database
#     assignToClusters()  # Assign users to clusters and save into database
#     clusters = Cluster.objects.all().values_list()
#     dataframe = pd.DataFrame.from_records(clusters,
#                                           columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
#                                                    'drivers', 'propositions'])
#     for cluster in dataframe.iloc:  # Run optimization on each cluster
#         optimize(cluster['idCluster'])