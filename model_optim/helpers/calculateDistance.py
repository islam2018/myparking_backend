import json

import requests
from sklearn.metrics.pairwise import haversine_distances
import pandas as pd
import numpy as np

from model_optim.helpers.matrixFormat import splitUsers, splitParkings


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


def calculateDistanceMatrix(dataframe, users): # users x parkings
    HERE_API_KEY = "SnEjiUueUMbL4zeFjvfi6vx4JMWGkdCrof7QDZLQWoY"

    class Object(object):
        pass

    uSplits = splitUsers(users)
    pSplits = splitParkings(dataframe)

    starts = []
    for part in uSplits:
        start = Object()
        index = 0
        for user in part:
            position = user[6]
            setattr(start, 'start' + str(index), str(position[0]) + ',' + str(position[1]))
            index = index + 1
        print(start.__dict__)
        starts.append(start)

    dests = []
    for part in pSplits:
        dest = Object()
        index = 0
        for parking in part:
            setattr(dest, 'destination' + str(index), str(parking[7]) + ',' + str(parking[8]))
            index = index + 1
        print(dest.__dict__)
        dests.append(dest)

    distances = [[0] * len(dataframe)] * len(users)

    offsetX = 0
    offsetY = 0
    for start in starts:
        offsetY = 0
        for dest in dests:
            travelResponse = requests.get("https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json",
                                          params={
                                              'apiKey': HERE_API_KEY,
                                              **start.__dict__,
                                              **dest.__dict__,
                                              'mode': 'balanced;car;traffic:enabled',
                                              'summaryAttributes': 'traveltime,distance'
                                          })
            json_travel_data = json.loads(travelResponse.text)
            matrix = json_travel_data['response']['matrixEntry']
            print(matrix)

            for i in matrix:
                X = i['startIndex'] + offsetX
                Y = i['destinationIndex'] + offsetY
                distances[X][Y] = i['summary']['distance']

            offsetY = offsetY + 100
        offsetX = offsetX + 15
    print(distances)
    d = np.asarray(distances)
    print(np.ma.size(d, axis=1))
    return distances
