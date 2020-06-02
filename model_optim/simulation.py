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
    # driver/updatePosition post [lat,long] this is it okey emb"d ki ndir all view calls ani ndirha
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
## filters #
MIN_PRICE = 10
MAX_PRICE = 200
MIN_DISTANCE = 20  # 20 meters of walking
MAX_DISTANCE = 1000


def main(_lambda, _num_events, use_optimisation):
    tracemalloc.start()  # to track memory usage
    _event_num = []
    _inter_event_times = []  # time between requests to wait tht time
    _event_times = []
    _event_time = 0
    print('EVENT_NUM,INTER_EVENT_T,EVENT_T')
    start = timeit.default_timer()
    user_ids = []
    recommended = []
    unsatisfied_users = 0
    for i in range(_num_events):
        _event_num.append(i)
        n = random.random()

        # Generate the inter-event time from the exponential distribution's CDF using the Inverse-CDF technique
        _inter_event_time = -math.log(1.0 - n) / _lambda
        # _inter_event_time = np.random.poisson(lam=_lambda, size=1)
        _inter_event_times.append(_inter_event_time)

        # Add the inter-event time to the running sum to get the next absolute event time
        _event_time = _event_time + _inter_event_time
        _event_times.append(_event_time)

        # wait generated inter_event_time before genrating next request
        # i wait tht time here
        # time.sleep(_inter_event_time)
        # get a random user
        # hna i select a user id randomly
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

        recommended = requestParkings(id_automobiliste=user_info[0], depart=depart, destination=destination,
                                      min_price=prix_min,
                                      max_price=prix_max,
                                      min_distance=distance_min, max_distance=distance_max, equipements=equipements,
                                      mode=use_optimisation)

        current, peak = tracemalloc.get_traced_memory()

        if not recommended:  # empty
            unsatisfied_users += 1
        else:
            # this
            updateSelectedParkingInfo(idParking=recommended[0])  # best option , considering list is ordered

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
    ## plot time arrival for pfe paper
    # fig = plt.figure()
    # #  fig.title('Temps absolu des événements consécutifs dans un processus simulé de Poisson')
    # plot, = plt.plot(_event_num, _event_times, 'bo-', label='Moment d\'arrivé d\'une demande de recherche')
    # plt.legend(handles=[plot])
    # plt.xlabel('Ordre de requête')
    # plt.ylabel('Temps')
    # plt.show()

    # fake data
    # _ram_percentage = "Ram " + str(_lambda) + "," + str(_num_events) + "," + str(use_case)
    # _uc_percentage = "UC " + str(_lambda) + "," + str(_num_events) + "," + str(use_case)
    # _occupancy_avg = "Occ " + str(_lambda) + "," + str(_num_events) + "," + str(use_case)
    # _satisfaction_avg = "Sat " + str(_lambda) + "," + str(_num_events) + "," + str(use_case)
    _ram_percentage = np.random.uniform(low=0.01, high=1)
    _uc_percentage = np.random.uniform(low=0.01, high=1)
    _occupancy_avg = random.randrange(1, 100)
    _satisfaction_avg = random.randrange(1, _num_events)
    return _ram_percentage, _uc_percentage, _occupancy_avg, _satisfaction_avg


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


def plotting(data):
    """ genère  8 graphes en utilisant data"""
    labels = ['30', '100', '1000']
    graph_labels = ['Optimisation & Clustering', 'Optimsation seulement', 'Pas d\'optimisation']
    graph_titles = [
        'Taux moyen d\'utilisation de mémoire - Trafic léger',
        'Taux moyen d\'utilisation du CPU - Trafic léger',
        'Taux moyen d\'occupation des parkings - Trafic léger',
        'Taux moyen des utilisateurs satisfés - Trafic léger',
        'Taux moyen d\'utilisation de mémoire - Trafic lourd',
        'Taux moyen d\'utilisation du CPU - Trafic lourd',
        'Taux moyen d\'occupation des parkings - Trafic lourd',
        'Taux moyen des utilisateurs satisfés - Trafic lourd',
    ]
    xAxeLabel = 'nombre de requêtes'
    yAxeLabels = ['% RAM', '% CPU', '% Occupation', '% Satisfaction']

    for index, title in enumerate(graph_titles):
        _case_1 = data[index][0:3]
        _case_2 = data[index][3:6]
        _case_3 = data[index][6:9]
        x = np.arange(len(labels))  # the labels locations
        width = 0.175  # width of bars
        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, _case_1, width, label=graph_labels[0])
        rects2 = ax.bar(x + width / 2, _case_2, width, label=graph_labels[1])
        rects3 = ax.bar(x + 3 * width / 2, _case_3, width, label=graph_labels[2])

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(yAxeLabels[index % 4])
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        fig.tight_layout()

        plt.show()

    # _light_traffic_ram_case_0 = data[0][0:3]
    # _light_traffic_ram_case_1 = data[0][3:6]
    # _light_traffic_ram_case_2 = data[0][6:9]
    #
    # x = np.arange(len(labels))  # the labels locations
    # width = 0.175  # width of bars
    # fig, ax = plt.subplots()
    # rects1 = ax.bar(x - width / 2, _light_traffic_ram_case_0, width, label='size_30')
    # rects2 = ax.bar(x + width / 2, _light_traffic_ram_case_1, width, label='size_100')
    # rects3 = ax.bar(x + 3 * width / 2, _light_traffic_ram_case_2, width, label='size_1000')
    #
    # # Add some text for labels, title and custom x-axis tick labels, etc.
    # ax.set_ylabel('% RAM')
    # ax.set_title('Taux moyen d\'utilisation de mémoire sur ')
    # ax.set_xticks(x)
    # ax.set_xticklabels(labels)
    # ax.legend()
    #
    # fig.tight_layout()
    #
    # plt.show()
    print("plotting the 4 graphs for rapport using the results_for_plots dataframe")
    print("histo of average parking occupancy, for 30, 100 ,1000 parkings, with and without optim")
    print("histo of average user satisfaction, for 30, 100 ,1000 parkings, with and without optim")
    print("histo of average ram usage, for 30, 100 ,1000 parkings, with and without optim/clusterin")
    print("histo of average uc usage, for 30, 100 ,1000 parkings, with and without optim/clusterin")


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, Automobiliste
    import pandas as pd

    process = psutil.Process(os.getpid())

    # results_for_plots = pd.DataFrame(
    #     data={'30': [0, 0, 0, 0], '100': [0, 0, 0, 0], '1000': [0, 0, 0, 0]})  # 4 rows for the 4 graphs
    # rateOfArrival = 5  # average number of automobliste in 1 h, can be heigher for heavier traffic
    # numberOfRequests = 100  # number of requests
    # use_optim = True  # use optimisation algorithmes
    # main(rateOfArrival, numberOfRequests, use_optim)
    # print(f"Current CPU usage ", process.cpu_percent())
    # plotting()  # using plots for results

    ## new process
    # simulation_data = [[""] * 4] * 8
    simulation_data = [[0] * 9 for x in range(8)]
    ratesOfArrival = [2, 10]
    sampleSizes = [10, 30, 50]
    methodsTested = [0, 1, 2]
    for index_row, _lambda in enumerate(ratesOfArrival):
        for index_column, _sampleSize in enumerate(sampleSizes):
            for use_case in methodsTested:
                j = index_column + 3 * use_case
                # ram_percentage, uc_percentage, occupancy_avg, satisfaction_avg = main(_lambda, _sampleSize, use_case)
                # tests ratios
                _ram_percentage = np.random.uniform(low=0.01, high=1)
                _uc_percentage = np.random.uniform(low=0.01, high=1)
                _occupancy_avg =  np.random.uniform(low=0.01, high=1)
                _satisfaction_avg =  np.random.uniform(low=0.01, high=1)
                simulation_data[index_row * 4][j] = _ram_percentage
                simulation_data[index_row * 4 + 1][j] = _uc_percentage
                simulation_data[index_row * 4 + 2][j] = _occupancy_avg
                simulation_data[index_row * 4 + 3][j] = _satisfaction_avg
    print("this is simuationdata")
    print(simulation_data)
    plotting(simulation_data)
    print(f"Current CPU usage ", process.cpu_percent())
