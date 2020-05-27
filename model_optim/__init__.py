from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction
import pandas as pd
from django.utils.timezone import now

from model_optim.assignement import assignToClusters
from model_optim.clustering import getParkingClusters
from model_optim.optimization import optimize
from model_optim.persistance import saveParkingsClusters, changeParkingDispo
from myparking_api.models import  Cluster


def runModel():
    with transaction.atomic():
        getParkingClusters()  # Clusetring and save into database
        assignToClusters()  # Assign users to clusters and save into database
        clusters = Cluster.objects.all().values_list()
        dataframe = pd.DataFrame.from_records(clusters,
                                              columns=['idCluster', 'label', 'centroid', 'reservations', 'parkings',
                                                       'drivers', 'propositions'])
        for cluster in dataframe.iloc:  # Run optimization on each cluster
            optimize(cluster['idCluster'])

def AFTER_SERVER_INIT():

    print("********RUNNING MODEL AT ",now()," **********")
    #Running this method each 5 minute to stay updated
    #runModel()

    scheduler = BackgroundScheduler()
    scheduler.add_job(runModel, 'interval', minutes =1)
    """For simulation purposes """
    #scheduler.add_job(changeParkingDispo, 'interval', minutes=1)
    """"""
    scheduler.start()