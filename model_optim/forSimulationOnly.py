'''FOR SIMULATION ONLY'''
import pandas as pd
import requests
from django.db.models import Case, When
from mip import minimize, xsum, OptimizationStatus, Model, BINARY

from model_optim import getParkingClusters, assignToClusters
from model_optim.helpers.calculateDistance import calculateDistanceMatrix
from model_optim.persistance import getReservations
from myparking_api.models import Cluster, Parking, Automobiliste, Reservation, Porposition
import numpy as np

mDataframe = None
mUsers = None
mAffectations = None


# this a new function (new file from me) oe=key okey hna li lazem teb3ini
def getTestRecommandations(driverId, mode):
    if (mode == 0):  # there is 3 modes first it searches for parkings using clusters et tout (like the app) okey ?
        # okey
        query = Cluster.objects.filter(drivers=driverId).values_list()
        clusters = pd.DataFrame.from_records(query,
                                             columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                                      'drivers',
                                                      'propositions'])
        cluster = clusters.iloc[0]
        propositions_ids = list(cluster['propositions'])
        print("automobilistId", driverId, propositions_ids)
        # dir order f la requete nn?  sorry machefht
        queryProp = Porposition.objects.filter(id__in=propositions_ids, automobiliste_id=driverId).values_list()
        #         ma n3rfchc jamais drtha  # yek haka superierue a? hhhh m stupid daymen >0
        # haka? ordre contraire zedt - ah oe=key thnx jamaois drtha
        # met toop att dkika nchof haja   mazel f l'autre  cas
        propositions = pd.DataFrame.from_records(queryProp,
                                                 columns=['idProposition', 'automobiliste', 'parking', 'value'])
        # i have a question u here?
        # cc oui ? hna f next steps yak tgardi l'ordre? what u mean next steps oui okey aya fhmni next case dok
        parkings_id = []
        parking_weights = []
        for proposition in propositions.iloc:  # ak sur m la selection de donnes? oui oui
            parkings_id.append(proposition['parking'])
            parking_weights.append(proposition['value'])
        # babe i need ur helphere kifech djib 2colns no wher? wkil haka att i check
        print(parkings_id) # mchi hna f optimize ani nhdr f update parking data , iknow mais
        return (Parking.objects.filter(id__in=parkings_id, nbPlacesLibres__gt=0), parkings_id, parking_weights)
    elif (
            mode == 1):
        # wait ndirlekr resume

        parkings_id = []
        parking_weights = []
        array = np.asarray(mAffectations)
        for ix, iy in np.ndindex(array.shape):
            idParking = mDataframe.iloc[iy]['ID']
            idAutomobiliste = mUsers.iloc[ix]['idAutomobiliste']
            if (int(idAutomobiliste) == int(driverId) and array[
                ix, iy] > 0):  # mm hna we have to sort the list mz ma fhmtni hadi ki tfhmna nsgmoha att
                parkings_id.append(idParking)
                parking_weights.append(array[ix, iy])
                print("idParking added", idParking)
        # bb b"thom separe w khls at

        return (Parking.objects.filter(id__in=parkings_id, nbPlacesLibres__gt=0), parkings_id, parking_weights)
    elif (mode == 2):
        return (Parking.objects.filter(nbPlacesLibres__gt=0),[],[])


NP = 0
NU = 0


# fahmek hadi 9bel , look this foction , optimize for all users and parkings , sans slusteing,
# kima li rana nsagmo fiha berk sans custerig look, fhamti ? yeah babe, mala lzm nsgmo hadi tan?oui of cours

def optimizeWithoutClustering():
    respons = requests.post("https://evaluataionmyparking.herokuapp.com/pusher/broadcast/driver", {
        'title': 'Started...',
        'body': 'Runing model without optim',
        'content': '',
        'interest': 'driver_notifs'
    })
    print(respons.text)
    global NP
    global NU
    global mDataframe
    global mUsers
    global mAffectations

    queryParkings = Parking.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(queryParkings,
                                          columns=['ID', 'NB_ETAGE', 'NB_PLACES', 'NB_PLACES_LIBRES', '4', '5', '6',
                                                   'LAT', 'LON', '9', '10', '11', '12', '13', '14'])
    print(dataframe)
    # filtered = parkingsInRadius(dataframe, center)

    queryUsers = Automobiliste.objects.all().values_list()
    users = pd.DataFrame.from_records(queryUsers,
                                      columns=['idAutomobiliste', 'compte', 'idCompte', 'nom', 'numTel',
                                               'prenom', 'position', 'auth', 'favoris'])
    print(users)
    NU = len(users)
    NP = len(dataframe)

    DISTANCES = calculateDistanceMatrix(dataframe, users)
    print(DISTANCES)

    RESERV = getReservationsWithoutClusters(dataframe, users)

    model = Model('Model_six_users')
    x = [[model.add_var(name='x' + str(i) + ',' + str(j), var_type=BINARY) for j in range(NP)] for i in range(NU)]

    model.objective = minimize(
        xsum(F(dataframe, DISTANCES, i, j) * x[i][j] for i in range(NU) for j in range(NP))
        + xsum(1
               + (1 / (NP ** 2)) * (xsum(x[i][j] for j in range(NP)) + xsum(
            x[i][j] and x[i][k] if j != k else 0 for j in range(NP) for k in range(NP)))
               - (2 / NP) * xsum(x[i][j] for j in range(NP))
               for i in range(NU))
        + xsum(1
               + (1 / (NU ** 2)) * (xsum(x[i][j] for i in range(NU)) + xsum(
            x[i][j] and x[k][j] if i != k else 0 for i in range(NU) for k in range(NU)))
               - (2 / NU) * xsum(x[i][j] for i in range(NU))
               for j in range(NP))
    )

    for r in RESERV:
        # print(r['i'], r['j'])
        model += x[r['i']][r['j']] == 1

    #   ahbsss win jbth hadi
    #   hdi lkdima '
    matrix_cout = [[F(dataframe, DISTANCES, i, j) for j in range(NP)] for i
                   in range(NU)]
    # each parking has enough space
    for j in range(NP):
        model += xsum(x[i][j] if (min(matrix_cout[i]) == matrix_cout[i][j]) else 0 for i in range(NU)) <= int(
            dataframe.iloc[j]['NB_PLACES_LIBRES'])  # haka? oui thnx i mean f wch lunt dir oui

    # for i in range(NU):
    #     model += xsum(x[i][j] for j in range(NP)) >= 1

    status = model.optimize()
    affectations = pd.DataFrame(columns=range(NP), index=range(NU))
    if status == OptimizationStatus.OPTIMAL:
        answer = 'optimal solution cost {} found'.format(model.objective_value)
    elif status == OptimizationStatus.FEASIBLE:
        answer = 'sol.cost {} found, best possible: {}'.format(model.objective_value, model.objective_bound)
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        answer = 'no feasible solution found, lower bound is: {}'.format(model.objective_bound)
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        for user in range(NU):
            for parking in range(NP):
                affectations[parking][user] = x[user][parking].x * matrix_cout[user][parking]
        for v in model.vars:
            answer += '{} : {}\n'.format(v.name, v.x)
            # print(v.name + " " + str(v.x))
    else:
        answer = "no solution"
    # print(x)
    print(affectations)
    mAffectations = affectations
    mDataframe = dataframe
    mUsers = users
    respons = requests.post("https://evaluataionmyparking.herokuapp.com/pusher/broadcast/driver", {
        'title': 'Finished...',
        'body': 'Runing model without optim finished',
        'content': '',
        'interest': 'driver_notifs'
    })
    print(respons.text)


def SommeDist(D, i):
    somme = 0
    for j in range(NP):
        somme = somme + D[i][j]
    return somme


def TauxDisp(dataframe, j):
    # u said hadi ? yeah w att wkli kayn max te3 column f dataframe t'es sur haka ? nn dok nconfirmi f la console
    max_nb = int(dataframe.max(0).loc['NB_PLACES'])  # asbr ani chaka f axis khls hadk howa
    # att we test ur ordering mehtod ki nas tan
    return dataframe.iloc[j]['NB_PLACES_LIBRES'] / max_nb  # yak kolna we use max mmm sah


def F(dataframe, D, i, j):
    val = 0.5 * (D[i][j] / SommeDist(D, i)) + 0.5 * (1 - TauxDisp(dataframe, j))
    print("cou", val)
    # print("F" + str(i) + "," + str(j) + " : " + str(val))
    return val ** 2


def getReservationsWithoutClusters(dataframe, users):
    reservations = Reservation.objects.all().values_list()
    reservations_array = np.asarray(reservations)
    RESERV = []
    print(dataframe)
    print(users)
    for res in reservations_array:
        try:
            i = dataframe.loc[dataframe['ID'] == res[12]].index[0]
            j = users.loc[users['idAutomobiliste'] == res[13]].index[0]
            print(i, j, 'ij indexex parking user for reserv')
            RESERV.append({
                'i': i,
                'j': j
            })
        except Exception:
            print("GET RESERVATION FOR MODEL ERRORR")
            pass

    return RESERV
# chehal tk3d hakak? 3 or 4 linutes okey
