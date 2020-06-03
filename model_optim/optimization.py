import pandas as pd
from mip import *
from model_optim.helpers.calculateDistance import calculateDistanceMatrix
from model_optim.persistance import getReservations, saveAffectations
from myparking_api.models import Cluster, Parking, Automobiliste

NP = 0
NU = 0


def SommeDist(D, i):
    somme = 0
    for j in range(NP):
        somme = somme + D[i][j]
    return somme


def TauxDisp(dataframe, j):
    # u said hadi ? yeah w att wkli kayn max te3 column f dataframe t'es sur haka ? nn dok nconfirmi f la console
    max_nb = int(dataframe.max(0).loc['NB_PLACES'])  # asbr ani chaka f axis khls hadk howa
    return dataframe.iloc[j]['NB_PLACES_LIBRES'] / max_nb  # yak kolna we use max mmm sah


# ma hlbtnich kml i feel disapointed, ): babe u know mahbestch ga3 mechi ze3ma ahabitch wela
# okey m3lich let's do them now
# att babe
def F(dataframe, D, i, j):
    val = 0.5 * (D[i][j] / SommeDist(D, i)) + 0.5 * (1 - TauxDisp(dataframe, j))
    print("cou", val)
    # print("F" + str(i) + "," + str(j) + " : " + str(val))
    return val ** 2


def optimize(idCluster):
    global NP
    global NU
    query = Cluster.objects.filter(id=idCluster).values_list()
    cluster = pd.DataFrame.from_records(query,
                                        columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                                 'drivers',
                                                 'propositions']).iloc[0]

    parkings_id = list(cluster['parkings'])
    queryParkings = Parking.objects.filter(id__in=parkings_id).values_list()
    dataframe = pd.DataFrame.from_records(queryParkings,
                                          columns=['ID', 'NB_ETAGE', 'NB_PLACES', 'NB_PLACES_LIBRES', '4', '5', '6',
                                                   'LAT', 'LON', '9', '10', '11', '12', '13', '14'])
    print(dataframe)
    # filtered = parkingsInRadius(dataframe, center)

    drivers_id = list(cluster['drivers'])
    queryUsers = Automobiliste.objects.filter(id__in=drivers_id).values_list()
    users = pd.DataFrame.from_records(queryUsers,
                                      columns=['idAutomobiliste', 'compte', 'idCompte', 'nom', 'numTel',
                                               'prenom', 'position', 'auth', 'favoris'])
    print(users)
    NU = len(users)
    NP = len(dataframe)

    DISTANCES = calculateDistanceMatrix(dataframe, users)
    print(DISTANCES)

    RESERV = getReservations(dataframe, users, cluster['idCluster'])

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
        print(r['i'], r['j'])
        model += x[r['i']][r['j']] == 1

    #      ma zdtch ma contrainte. ? ah nn  oui  mazel ma zedtha sorry
    # mchi , pcq fiha drt array fih les F hadok kml ama branche rahi fiha ?
    # att nchof
    # # chkit model optim hali githubb ndji ok dok njibha hh
    # for j in range(NP):
    #     print('libre ', dataframe.iloc[j]['NB_PLACES_LIBRES'])
    #     model += xsum(x[i][j] for i in range(NU)) <= int(dataframe.iloc[j]['NB_PLACES_LIBRES'])

    ## start
    # erwh hna ni djit babe att c koi ca
    ## att F don"t know 3lach i didn"t use it direct hhh
    ## drt array  2d fih kml les F chatra
    # at nrj3ha using F ani nktb aaah
    # ggggg don't write att nchouf hadja
    # D wsmha hna ?
    # ehdr thanx
    matrix_cout = [[F(dataframe, DISTANCES, i, j) for j in range(NP)] for i
                   in range(NU)]
    # each parking has enough space
    for j in range(NP):
        model += xsum(x[i][j] if (min(matrix_cout[i]) == matrix_cout[i][j]) else 0 for i in range(NU)) <= int(
            dataframe.iloc[j]['NB_PLACES_LIBRES'])  # haka? oui thnx i mean f wch lunt dir oui
    ## end

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
                affectations[parking][user] = (x[user][parking].x) * matrix_cout[user][parking]
        for v in model.vars:
            answer += '{} : {}\n'.format(v.name, v.x)
            print(v.name + " " + str(v.x))
    else:
        answer = "no solution"
    # print(x)
    print(affectations)
    saveAffectations(dataframe, users, affectations, cluster['idCluster'])
    return affectations
