
'''FOR SIMULATION ONLY'''
import pandas as pd
from mip import minimize, xsum, OptimizationStatus, Model, BINARY

from model_optim import getParkingClusters, assignToClusters
from model_optim.helpers.calculateDistance import calculateDistanceMatrix
from model_optim.persistance import  getReservations
from myparking_api.models import Cluster, Parking, Automobiliste, Reservation, Porposition
import numpy as np

mDataframe =None
mUsers = None
mAffectations = None

def getTestRecommandations(driverId, mode):
    if (mode==0):
        query = Cluster.objects.filter(drivers=driverId).values_list()
        clusters = pd.DataFrame.from_records(query,
                                             columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                                      'drivers',
                                                      'propositions'])
        cluster = clusters.iloc[0]
        propositions_ids = list(cluster['propositions'])
        print("automobilistId", driverId, propositions_ids)
        queryProp = Porposition.objects.filter(id__in=propositions_ids, automobiliste_id=driverId).values_list()
        propositions = pd.DataFrame.from_records(queryProp,
                                                 columns=['idProposition', 'automobiliste', 'parking', 'value'])
        parking_ids = propositions['parking'].to_list()
        print(parking_ids)
        return Parking.objects.filter(id__in=parking_ids)
    elif (mode==1):
        parkings_id = []
        array = np.asarray(mAffectations)
        for ix, iy in np.ndindex(array.shape):
            idParking = mDataframe.iloc[iy]['ID']
            idAutomobiliste = mUsers.iloc[ix]['idAutomobiliste']
            if (int(idAutomobiliste) == int(driverId) and array[ix, iy] == 1):
                parkings_id.append(idParking)
                print("idParking added", idParking)
        return Parking.objects.filter(id__in=parkings_id)
    elif (mode==2):
        return Parking.objects.all()



NP = 0
NU = 0
def optimizeWithoutClustering():
    global NP
    global NU
    global mDataframe
    global mUsers
    global mAffectations

    queryParkings = Parking.objects.all().values_list()
    dataframe = pd.DataFrame.from_records(queryParkings,columns=['ID','NB_ETAGE','NB_PLACES','NB_PLACES_LIBRES','4','5','6','LAT','LON','9','10','11','12','13','14'])
    print(dataframe)
    #filtered = parkingsInRadius(dataframe, center)

    queryUsers = Automobiliste.objects.all().values_list()
    users = pd.DataFrame.from_records(queryUsers,
                                     columns=['idAutomobiliste', 'compte', 'idCompte', 'nom', 'numTel',
                                              'prenom', 'position', 'auth', 'favoris'])
    print(users)
    NU = len(users)
    NP = len(dataframe)

    DISTANCES = calculateDistanceMatrix(dataframe,users)
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

    #       '
    for j in range(NP):
        # print('libre ', dataframe.iloc[j]['NB_PLACES_LIBRES'])
        model += xsum(x[i][j] for i in range(NU)) <= int(dataframe.iloc[j]['NB_PLACES_LIBRES'])

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
                affectations[parking][user] = x[user][parking].x
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


def SommeDist(D, i):
    somme = 0
    for j in range(NP):
        somme = somme + D[i][j]
    return somme

def TauxDisp(dataframe, j):
    return dataframe.iloc[j]['NB_PLACES_LIBRES'] / dataframe.iloc[j]['NB_PLACES']

def F(dataframe, D, i, j ):
    val = 0.5 * (D[i][j] / SommeDist(D, i)) + 0.5 * (1 - TauxDisp(dataframe, j))
    print("cou",val)
    # print("F" + str(i) + "," + str(j) + " : " + str(val))
    return val**2


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
            print(i,j, 'ij indexex parking user for reserv')
            RESERV.append({
                'i': i,
                'j': j
            })
        except Exception:
            print("GET RESERVATION FOR MODEL ERRORR")
            pass

    return RESERV