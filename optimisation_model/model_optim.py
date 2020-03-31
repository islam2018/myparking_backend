from mip import *

from optimisation_model.prepareInputData import getDistanceMatrix

NU = 60 # nb users
NP = 20  # nb parkings

class Object(object):
    pass

# D = [[5, 10, 18, 12, 80],
#      [6, 9, 5, 95, 12],
#      [54, 10, 12, 17, 23],
#      [7, 15, 18, 15, 20],
#      [10, 11, 65, 12, 41],
#      [18, 16, 34, 18, 31]]
# PLACES_LIBRES = [3, 4, 2, 3, 5]
# NB_PLACES = [7, 5, 5, 3, 10]


def SommeDist(D, i):
    somme = 0
    for j in range(NP):
        somme = somme + D[i][j]
    return somme


def TauxDisp(PLACES_LIBRES, NB_PLACES, j):
    return PLACES_LIBRES[j] / NB_PLACES[j]


def F(D, PLACES_LIBRES, NB_PLACES, i, j):
    val = 0.5 * (D[i][j] / SommeDist(D, i)) + 0.5 * (1 - TauxDisp(PLACES_LIBRES, NB_PLACES, j))
    print("F" + str(i) + "," + str(j) + " : " + str(val))
    return val


def optimize():
    model = Model()
    answer = Object()
    D, NB_PLACES, PLACES_LIBRES = getDistanceMatrix(NU, NP)

    # decision variable
    x = [[model.add_var(name='x' + str(i) + ',' + str(j), var_type=BINARY) for j in range(NP)] for i in range(NU)]

    # objective function
    model.objective = minimize(
        xsum(F(D, PLACES_LIBRES, NB_PLACES, i, j) * x[i][j] for i in range(NU) for j in range(NP))
        + xsum(((NP - xsum(x[i][j] for j in range(NP))) / NP) for i in range(NU))
        + xsum(((NU - xsum(x[i][j] for i in range(NU))) / NU) for j in range(NP))
    )

    # each parking has enough space
    for j in range(NP):
        model += xsum(x[i][j] for i in range(NU)) <= PLACES_LIBRES[j]

    # each user has at least 2 proposisionts
    # for i in range(NU):
    #     model += xsum(x[i][j] for j in range(NP)) >= 2

    status = model.optimize()

    # if status == OptimizationStatus.OPTIMAL:
    #     answer = 'optimal solution cost {} found'.format(model.objective_value)
    # elif status == OptimizationStatus.FEASIBLE:
    #     answer = 'sol.cost {} found, best possible: {}'.format(model.objective_value, model.objective_bound)
    # elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    #     answer = 'no feasible solution found, lower bound is: {}'.format(model.objective_bound)
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        for user in range(0, NU):
            print("this is x",x[0][0].x)
            ligne = Object()
            for parking in range(0, NP):
                setattr(ligne,str(parking),x[user][parking].x)
            setattr(answer, str(user), ligne.__dict__)
    return answer.__dict__

# print(optimize())