import pandas as pd

from myparking_api.models import Cluster, Porposition, Parking


def getRecomendedParkings(idAutomobiliste): #return a querySet
    query = Cluster.objects.filter(drivers=idAutomobiliste).values_list()
    cluster = pd.DataFrame.from_records(query,
                                        columns=['idCluster', 'label', 'centroid','reservations', 'parkings', 'drivers',
                                                 'propositions']).iloc[0]
    propositions_ids= list(cluster['propositions'])
    queryProp = Porposition.objects.filter(id__in=propositions_ids, automobiliste_id=idAutomobiliste).values_list()
    propositions = pd.DataFrame.from_records(queryProp,
                                        columns=['idProposition', 'automobiliste', 'parking', 'value'])
    parking_ids = propositions['parking'].to_list()
    print(parking_ids)
    return Parking.objects.filter(id__in=parking_ids)