from shapely.geometry import MultiPoint
from geopy.distance import great_circle

def get_centermost_point(cluster):  # c luster = dataframe[['LAG', 'LON']].to_numpy()
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)