
from sklearn.metrics.pairwise import haversine_distances
import pandas as pd
import numpy as np

def calculateDistance(df, min_samples):  # n samples, 2 features
    new_df_rd = np.radians(df[['LAT', 'LON']].to_numpy())
    matrix = haversine_distances(new_df_rd, new_df_rd)
    matrix_df = pd.DataFrame(matrix)
    new_matrix = matrix * 6371.0088
    for i in range(df.shape[0]):
        new_matrix[i].__imul__(
            min_samples / int(df.iloc[i]['NB_PLACES_LIBRES']))  # we can improve here for more logical weighted positions
        new_matrix[:, i].__imul__(min_samples / int(df.iloc[i]['NB_PLACES_LIBRES']))
        new_matrix[0][0] = 0.0
    return new_matrix