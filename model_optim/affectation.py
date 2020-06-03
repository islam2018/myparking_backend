import pandas as pd
from model_optim import runModel
from myparking_api.models import Porposition, Parking, Cluster


def getRecomendedParkings(idAutomobiliste): #return a querySet
    query = Cluster.objects.filter(drivers=idAutomobiliste).values_list()
    clusters = pd.DataFrame.from_records(query,
                                        columns=['idCluster', 'label', 'centroid','reservations', 'parkings', 'drivers',
                                                 'propositions'])
    if (clusters.size>0):
        cluster = clusters.iloc[0]
        propositions_ids = list(cluster['propositions'])
        print("automobilistId",idAutomobiliste, propositions_ids)
        queryProp = Porposition.objects.filter(id__in=propositions_ids, automobiliste_id=idAutomobiliste).values_list()
        propositions = pd.DataFrame.from_records(queryProp,
                                                 columns=['idProposition', 'automobiliste', 'parking', 'value'])
        only_ids = propositions['parking'].to_list()
        # doka only ids tan trj3ha nn? manich hab ni hab nkhedjha fl view bech maneb3tch lot of daa
        # pcq jik w3ra t3d tkhrja frm dict, sinn ab3t parking sids as dataframe
        #meditli idée mdit la solutoon hh dataframe kbir non
        parkings_id = []
        parking_weights= []
        print(parkings_id)
        # u'r using same list for diff type of content
        for proposition in propositions.iloc:  # ak sur m la selection de donnes? oui oui
            parkings_id.append(proposition['parking'])
            parking_weights.append(proposition['value'])
            # asbr bb 3lch ak dyr haka
        return (Parking.objects.filter(id__in=parkings_id,nbPlacesLibres__gt=0),parkings_id,parking_weights)
    else:
        runModel()
        return getRecomendedParkings(int(idAutomobiliste))

