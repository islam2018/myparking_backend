import os
import random
import math
import statistics
import time
import timeit
import tracemalloc

import matplotlib.pyplot as plt
import numpy as np
import psutil as psutil
import requests

from model_optim.helpers.simulationData import generateNearbyGPSPosition


def generateRandomFiltersValues():
    equipements_in_bdd = [1, 2, 3, 4, 5, 6, 7, 8]
    min_prix = np.random.uniform(MIN_PRICE, MIN_PRICE + 89)  # min entr 10 et 100
    max_prix = np.random.uniform(MAX_PRICE - 50, MAX_PRICE)  # max entre 130 et 200
    min_distance = np.random.uniform(MIN_DISTANCE, MIN_DISTANCE + 200)  # min entre 50 and 250 meters
    max_distance = np.random.uniform(MAX_DISTANCE - 200, MAX_DISTANCE)  # min entre 800 and 1000 meters
    equipements_ids = random.sample(equipements_in_bdd, k=random.randrange(1, 9))
    return min_prix, max_prix, min_distance, max_distance, equipements_ids


def updateUserBDD(id_automobliste, new_position):
    print("updating automobiliste position using islam's route" + str(id_automobliste) + ' ' + str(new_position))
    response = requests.post('/driver/updateLocation',{
        'driverId': int(id_automobliste),
        'lat' : new_position[0],
        'long' : new_position[1]
    })
    print(response)


def requestParkings(id_automobiliste, depart, destination, min_price, max_price, min_distance, max_distance, equipements,
                    mode):
    response = requests.get('/getParkings', {
        'mode': int(mode),
        'automobiliste': int(id_automobiliste),
        'start': depart,
        'destination': destination,
        'minDistance': min_distance,
        'maxDistance': max_distance,
        'minPrice': min_price,
        'maxPrice': max_price,
        'equipements': equipements
    })
    return response


def updateSelectedParkingInfo(idParking):
    parking = Parking.objects.get(id=idParking)
    parking.nbPlacesLibres= parking.nbPlacesLibres-1
    parking.save()
    # update nb places --


NB_USERS = 300
NB_PARKINGS = 100
NEARBY_RADIUS = 3000  # 3 km
## filters
MIN_PRICE = 10
MAX_PRICE = 200
MIN_DISTANCE = 20  # 20 meters of walking
MAX_DISTANCE = 1000


def main(_lambda, _num_events, use_optimisation):
    tracemalloc.start()  # to track memory usage
    _event_num = []
    _inter_event_times = []
    _event_times = []
    _event_time = 0
    print('EVENT_NUM,INTER_EVENT_T,EVENT_T')
    start = timeit.default_timer()
    user_ids = []
    recommended = []  # ids of recomended parkings
    unsatisfied_users = 0
    for i in range(_num_events):
        _event_num.append(i)
        # Get a random probability value from the uniform distribution's PDF
        n = random.random()

        # Generate the inter-event time from the exponential distribution's CDF using the Inverse-CDF technique
        _inter_event_time = -math.log(1.0 - n) / _lambda
        # _inter_event_time = np.random.poisson(lam=_lambda, size=1)
        _inter_event_times.append(_inter_event_time)

        # Add the inter-event time to the running sum to get the next absolute event time
        _event_time = _event_time + _inter_event_time
        _event_times.append(_event_time)

        # wait generated inter_event_time before genrating next request
        time.sleep(_inter_event_time)
        # get a random user
        user_info = None
        while user_info is None:
            user = list(Automobiliste.objects.all().values_list()[random.randrange(0, NB_USERS)])
            if not (user_ids.__contains__(user[0])):
                user_info = user
        print("selected user " + str(user_info[0]))
        user_ids.append(user_info[0])  # id automobiliste
        depart = generateNearbyGPSPosition(NEARBY_RADIUS, user_info[6][0], user_info[6][1])  # lat, lon
        destination = generateNearbyGPSPosition(NEARBY_RADIUS, depart[0], depart[1])  # lat, lon
        prix_min, prix_max, distance_min, distance_max, equipements = generateRandomFiltersValues()
        updateUserBDD(id_automobliste=user_info[0], new_position=depart)
        # generate request function here

        recommended = requestParkings(id_automobiliste=user_info[0], depart=depart, destination=destination,
                                      min_price=prix_min,
                                      max_price=prix_max,
                                      min_distance=distance_min, max_distance=distance_max, equipements=equipements,
                                      mode=use_optimisation)
        current, peak = tracemalloc.get_traced_memory()

        if not recommended:  # empty
            unsatisfied_users += 1
        else:
            updateSelectedParkingInfo(idParking=recommended[0])
        # print it all out
        print("Automibliste number : " + str(
            i) + ' arrived  after ' + '%.2f' % _inter_event_time + ' - at time t0 + ' + "%.2f" % _event_time)
        print('Request: id: ' + str(user_info[0]) + ' /start : ' + str(start) + ' /destination : ' + str(
            destination) + '/equipements : ' + str(
            equipements))
        print('\t\t prix in [{}, {}] distance in [{}, {}]'.format(prix_min, prix_max, distance_min, distance_max))
    stop = timeit.default_timer()
    print('Time of simulation : ', stop - start)
    print(f"Current Memroy usage for request is {current / 10 ** 6}MB; Peak was : {peak / 10 ** 6}MB")

    tracemalloc.stop()
    fig = plt.figure()
    #  fig.title('Temps absolu des événements consécutifs dans un processus simulé de Poisson')
    plot, = plt.plot(_event_num, _event_times, 'bo-', label='Moment d\'arrivé d\'une demande de recherche')
    plt.legend(handles=[plot])
    plt.xlabel('Ordre de requête')
    plt.ylabel('Temps')
    plt.show()


# plot the inter-event times
# fig = plt.figure()
# fig.suptitle('Times between consecutive events in a simulated Poisson process')
# plot, = plt.plot(_event_num, _inter_event_times, 'bo-', label='Inter-event time')
# plt.legend(handles=[plot])
# plt.xlabel('Index of event')
# plt.ylabel('Time')
# plt.show()
#
# # plot the absolute event times
# fig = plt.figure()
# fig.suptitle('Absolute times of consecutive events in a simulated Poisson process')
# plot, = plt.plot(_event_num, _event_times, 'bo-', label='Absolute time of event')
# plt.legend(handles=[plot])
# plt.xlabel('Index of event')
# plt.ylabel('Time')
# plt.show()
#
# _interval_nums = []
# _num_events_in_interval = []
# _interval_num = 1 # each 1 min is an interval
# _num_events = 0
#
# print('INTERVAL_NUM,NUM_EVENTS')
#
# for i in range(len(_event_times)):
#     _event_time = _event_times[i]
#     if _event_time <= _interval_num:
#         _num_events += 1
#     else:
#         _interval_nums.append(_interval_num)
#         _num_events_in_interval.append(_num_events)
#
#         print(str(_interval_num) + ',' + str(_num_events))
#
#         _interval_num += 1
#
#         _num_events = 1
#
# # print the mean number of events per unit time
# print(statistics.mean(_num_events_in_interval)) # number of events per minut
#
# # plot the number of events in consecutive intervals
# fig = plt.figure()
# fig.suptitle('Number of events occurring in consecutive intervals in a simulated Poisson process')
# plt.bar(_interval_nums, _num_events_in_interval)
# plt.xlabel('Index of interval')
# plt.ylabel('Number of events')
# plt.show()


def plotting():
    print("plotting")


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, Automobiliste
    import pandas as pd

    process = psutil.Process(os.getpid())
    results_for_plots = pd.DataFrame(data={'30': [0, 0, 0, 0], '100': [0, 0, 0, 0], '1000': [0, 0, 0, 0]})
    rateOfArrival = 5  # average number of automobliste in 1 h, can be heigher for heavier traffic
    numberOfRequests = 100  # number of requests
    use_optim = True  # use optimisation algorithmes
    main(rateOfArrival, numberOfRequests, use_optim)
    print(f"Current CPU usage ", process.cpu_percent())
    plotting()
