import math
import sqlite3

# import numpy as np
from math import radians, cos, sin, asin, sqrt
import pandas as pd

R = 6367  # earth radius
# destination = [36.789606, 3.057103]  # we can specify each user's destination later
radius = 2  # parkings within 2km radius of the destination


def haversine(row, destination1):
    lon1 = destination1[1]
    lat1 = destination1[0]
    lon2 = row['longitude']
    lat2 = row['lattitude']
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = R * c
    return km


def parkingsInRadius(parkings, destination):
    destination1 = [float(destination.split(',')[0]),float(destination.split(',')[1])]
    df = pd.DataFrame(list(parkings.values()))
    df['distance'] = df.apply(lambda row: haversine(row, destination1), axis=1)
    filteredDf = df.query('distance < ' + str(radius))
    parkings_ids = list(filteredDf['id'].to_numpy())
    return parkings.filter(id__in=parkings_ids)

# if __name__ == '__main__':
#     import time
#     start_time = time.time()
#     conn = sqlite3.connect('test.db')
#     dataframe = pd.read_sql_query('SELECT ID, LON, LAG FROM PARKING', conn)
#     test(dataframe)
#     print("--- %s seconds ---" % (time.time() - start_time))
#     conn.close()
