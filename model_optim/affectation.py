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
        parking_ids = propositions['parking'].to_list()
        print(parking_ids)
        return Parking.objects.filter(id__in=parking_ids)
    else:
        runModel()
        return getRecomendedParkings(int(idAutomobiliste))

