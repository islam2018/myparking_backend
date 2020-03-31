import math
import sqlite3

from geopy.distance import great_circle  # distance haversine
import pandas as pd
from shapely.geometry import MultiPoint
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances
import pandas as pd
import numpy as np


def get_centermost_point(cluster):  # c luster = dataframe[['LAG', 'LON']].to_numpy()
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def parkingsInRadius(df, centeroid, radius=10):
    df['distance'] = df.apply(lambda row: great_circle(row[['lattitude', 'longitude']], centeroid), axis=1)
    filteredDf = df.query('distance < ' + str(radius))
    return filteredDf


def distanceMatrixForClustering(df, min_samples):  # n samples, 2 features
    new_df_rd = np.radians(df[['lattitude', 'longitude']].to_numpy())
    matrix = haversine_distances(new_df_rd, new_df_rd)
    matrix_df = pd.DataFrame(matrix)
    new_matrix = matrix * 6371.0088
    for i in range(df.shape[0]):
        new_matrix[i].__imul__(
            min_samples/ df.iloc[i]['nbPlacesDisponibles']**2)  # we can improve here for more logical weighted positions
        new_matrix[:, i].__imul__(min_samples/ df.iloc[i]['nbPlacesDisponibles']**2)
        new_matrix[0][0] = 0.0
    return new_matrix
