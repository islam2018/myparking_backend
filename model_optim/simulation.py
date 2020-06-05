import json
import os
import random
import math
import threading
import time
import timeit
import tracemalloc
from io import BytesIO
import cloudinary
import cloudinary.uploader
import cloudinary.api
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
import requests
from model_optim.helpers.simulationData import generateNearbyGPSPosition
from myparking_api.models import Automobiliste, Parking


class TestThread(threading.Thread):
    def __init__(self, threadID, name, delay, user_info, mode):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.user_info = user_info
        self.mode = mode

    def run(self):
        print("Starting " + self.name)
        executeUserRequest(self.name, self.delay, self.user_info, self.mode)


def generateRandomFiltersValues():
    equipements_in_bdd = [1, 2, 3, 4, 5, 6, 7, 8]
    min_prix = np.random.uniform(MIN_PRICE, MIN_PRICE + 89)  # min entr 10 et 100
    max_prix = np.random.uniform(MAX_PRICE - 50, MAX_PRICE)  # max entre 130 et 200
    min_distance = np.random.uniform(MIN_DISTANCE, MIN_DISTANCE + 200)  # min entre 50 and 250 meters
    max_distance = np.random.uniform(MAX_DISTANCE - 200, MAX_DISTANCE)  # min entre 800 and 1000 meters
    equipements_ids = random.sample(equipements_in_bdd, k=random.randrange(1, 9))
    equipements_ids_str = ",".join(map(str, equipements_ids))
    print(equipements_ids_str)
    return min_prix, max_prix, min_distance, max_distance, equipements_ids_str


def updateUserBDD(id_automobliste, new_position):
    print("updating automobiliste position using islam's route" + str(id_automobliste) + ' ' + str(new_position))
    response = requests.post('https://evaluataionmyparking.herokuapp.com/driver/updateLocation', {
        'driverId': int(id_automobliste),
        'lat': new_position[0],
        'long': new_position[1]
    })
    print(response)


def getParkingOccupancyAvg():
    parkings_q = Parking.objects.all().values_list()
    parking_list = pd.DataFrame.from_records(parkings_q,
                                             columns=['ID', 'NB_ETAGE', 'NB_PLACES', 'NB_PLACES_LIBRES', '4', '5', '6',
                                                      'LAT', 'LON', '9', '10', '11', '12', '13', '14'])
    parking_list['parking_occupancy_rate'] = parking_list.apply(
        lambda row: (row.NB_PLACES - row.NB_PLACES_LIBRES) / row.NB_PLACES, axis=1)
    return parking_list['parking_occupancy_rate'].mean()


def requestParkings(id_automobiliste, depart, destination, min_price, max_price, min_distance, max_distance,
                    equipements,
                    mode):
    response = requests.get('https://evaluataionmyparking.herokuapp.com/getParkings', {
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


def updateSelectedParkingInfo(idParking, amount):  # increment decrement
    parking = Parking.objects.get(id=idParking)
    if amount < 0 < parking.nbPlacesLibres:  # cbon
        parking.nbPlacesLibres = parking.nbPlacesLibres + amount
        parking.save()
    else:
        if amount > 0 and parking.nbPlacesLibres < parking.nbPlaces:
            parking.nbPlacesLibres = parking.nbPlacesLibres + amount
            parking.save()


def resetNBplacesLibres():
    parkings = Parking.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(parkings,
                                          columns=['ID', 'NB_ETAGE', 'NB_PLACES', 'NB_PLACES_LIBRES', '4', '5', '6',
                                                   'LAT', 'LON', '9', '10', '11', '12', '13', '14'])
    map(resetOneParking, dataframe.iloc)


def resetOneParking(instance):
    p = Parking.objects.get(id=instance['ID'])
    p.nbPlacesLibres = random.randint(0, instance['NB_PLACES'])
    p.save()


def estimateDelayTime_EXP(rate):
    max_time = 300.0  # 5 hours for test purposes (minuts in test)
    n = random.random()  # genearte a random probability
    # Generate the inter-event time from the exponential distribution's CDF using the Inverse-CDF technique
    _inter_event_time = -math.log(1.0 - n) / rate
    return min(_inter_event_time, max_time)


def executeUserRequest(threadName, delay, user_info, mode):
    global memory_usage
    global uc_usage
    global unsatisfied_users
    tracemalloc.start()
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None)
    _gama = 30  # travel time is 30 min on average
    _mu = 60  # parking occupancy time is 60 min on average
    recommended = []
    # wait request arrival time
    time.sleep(delay)
    print("Executing user request %s: waited: %s , Now: %s" % (threadName, delay, time.ctime(time.time())))
    # request here
    depart = generateNearbyGPSPosition(NEARBY_RADIUS, float(user_info[6][0]), float(user_info[6][1]))  # lat, lon
    destination = generateNearbyGPSPosition(NEARBY_RADIUS, float(depart[0]), float(depart[1]))  # lat, lon
    prix_min, prix_max, distance_min, distance_max, equipements = generateRandomFiltersValues()
    updateUserBDD(id_automobliste=user_info[0], new_position=depart)
    res_getparkings = requestParkings(id_automobiliste=user_info[0], depart=depart, destination=destination,
                                      min_price=prix_min,
                                      max_price=prix_max,
                                      min_distance=distance_min, max_distance=distance_max, equipements=equipements,
                                      mode=mode)
    recommended = json.loads(res_getparkings.text)
    if not recommended:  # empty
        unsatisfied_users += 1
    else:
        # user found result and is gonna park
        travelTime = estimateDelayTime_EXP(rate=1 / _gama)  # time to reach parking
        time.sleep(travelTime)
        # user parks so availability -1
        updateSelectedParkingInfo(
            idParking=recommended[0]['idParking'], amount=-1)
        parkingTime = estimateDelayTime_EXP(rate=1 / _mu)  # time spent in parking
        time.sleep(parkingTime)
        # user leaving parking spot, so +1
        updateSelectedParkingInfo(
            idParking=recommended[0]['idParking'], amount=1)
    # collect memory and uc of current request

    current, peak = tracemalloc.get_traced_memory()
    memory_usage.append(current)
    uc_usage.append(process.cpu_percent(interval=None))


NB_USERS = 300
NB_PARKINGS = 100
NEARBY_RADIUS = 3000  # 3 km
# filter
MIN_PRICE = 10
MAX_PRICE = 200
MIN_DISTANCE = 20  # 20 meters of walking
MAX_DISTANCE = 1000
MAX_RAM = 1000  # to fetch later

# shared between threads
memory_usage = []
uc_usage = []
unsatisfied_users = 0


def main(_lambda, _num_events, use_optimisation):
    _event_num = []
    _inter_event_times = []
    _event_times = []
    _event_time = 0
    print('EVENT_NUM,INTER_EVENT_T,EVENT_T')
    start = timeit.default_timer()
    user_ids = []
    threads = []

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

        user_info = list(Automobiliste.objects.all().values_list()[random.randrange(0, NB_USERS)])
        user_ids.append(user_info[0])  # id automobiliste

        # threading
        user_request_thread = TestThread(i, f"Thread - {i}", _inter_event_time, user_info, use_optimisation)
        user_request_thread.start()  # starting thread for request
        threads.append(user_request_thread)

    stop = timeit.default_timer()
    print('Time of simulation : ', stop - start)

    tracemalloc.stop()
    for t in threads:
        t.join()
    # all requests are treated
    print(f" usage ram {memory_usage}")
    print(f" uc usage {uc_usage}")
    _ram_percentage = sum(memory_usage) / len(memory_usage)
    _uc_percentage = sum(uc_usage) / len(uc_usage)
    # _ram_percentage = (current / 10 ** 6) / MAX_RAM
    # _uc_percentage = process.cpu_percent(interval=None)
    # _occupancy_avg = getParkingOccupancyAvg()
    # _satisfaction_avg = unsatisfied_users / _num_events
    _occupancy_avg = random.random()
    _satisfaction_avg = random.random()
    return _ram_percentage, _uc_percentage, _occupancy_avg, _satisfaction_avg


def plotting(data):
    """ genère  8 graphes en utilisant data"""
    labels = ['10', '40', '100']  # write here babe, kima kotlk madam ha nruniw 3ndna o
    graph_labels = ['Optimisation & Clustering', 'Optimisation seulement', 'Méthode naive']
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
        # hada wech zedti berk ? yeah att ntesitw les graph fast
        # plt.savefig(f'test_results/{index}')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        res = cloudinary.uploader.upload(buffer, folder='test_figures')
        respons = requests.post("https://evaluataionmyparking.herokuapp.com/pusher/broadcast/driver",{
            'title': ' TEST: Evaluation et test',
            'body': 'Results are plotted, check cloudinary',
            'content': '',
            'interest': 'driver_notifs'
        })
        print(respons.text)
    # plt.show()

def main_test_fun():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, Automobiliste
    import pandas as pd

    # new process

    mem = psutil.virtual_memory()
    MAX_RAM = mem.total / 10 ** 6

    simulation_data = [[0] * 9 for x in range(8)]
    ratesOfArrival = [2, 5]
    sampleSizes = [10, 40, 100]
    methodsTested = [0, 1]  # here are methods
    for index_row, _lambda in enumerate(ratesOfArrival):
        for index_column, _sampleSize in enumerate(sampleSizes):
            for use_case in methodsTested:
                j = index_column + 3 * use_case
                memory_usage = []
                uc_usage = []
                unsatisfied_users = 0
                ram_percentage, uc_percentage, occupancy_avg, satisfaction_avg = main(_lambda, _sampleSize, use_case)

                # tests ratios
                # ram_percentage = np.random.uniform(low=0.01, high=1)
                # uc_percentage = np.random.uniform(low=0.01, high=1)
                # occupancy_avg = np.random.uniform(low=0.01, high=1)
                # satisfaction_avg = np.random.uniform(low=0.01, high=1)
                simulation_data[index_row * 4][j] = ram_percentage
                simulation_data[index_row * 4 + 1][j] = uc_percentage
                simulation_data[index_row * 4 + 2][j] = occupancy_avg
                simulation_data[index_row * 4 + 3][j] = satisfaction_avg
                resetNBplacesLibres()
        print("work for mode 2")
        # ram_percentage = np.random.uniform(low=0.01, high=1)
        # uc_percentage = np.random.uniform(low=0.01, high=1)
        # occupancy_avg = np.random.uniform(low=0.01, high=1)
        # satisfaction_avg = np.random.uniform(low=0.01, high=1)
        memory_usage = []
        uc_usage = []
        unsatisfied_users = 0
        ram_percentage, uc_percentage, occupancy_avg, satisfaction_avg = main(_lambda, 100, 2)
        for j in range(6, 9):
            simulation_data[index_row * 4][j] = ram_percentage
            simulation_data[index_row * 4 + 1][j] = uc_percentage
            simulation_data[index_row * 4 + 2][j] = occupancy_avg
            simulation_data[index_row * 4 + 3][j] = satisfaction_avg
            resetNBplacesLibres()

    print("this is simuationdata")

    print(simulation_data)
    plotting(simulation_data)
    # print(f"Current CPU usage ", process.cpu_percent(interval=None))

# if __name__ == '__main__':
#     main_test_fun()


