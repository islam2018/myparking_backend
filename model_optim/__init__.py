# from myparking.wsgi import *
from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction


def AFTER_SERVER_INIT():
    import pandas as pd
    from model_optim.assignement import assignToClusters
    from model_optim.clustering import getParkingClusters
    from model_optim.optimization import optimize
    from model_optim.persistance import saveParkingsClusters, changeParkingDispo
    from myparking_api.models import Cluster

    # Running this method each 5 minute to stay updated
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

    scheduler = BackgroundScheduler()
    scheduler.add_job(runModel, 'interval', minutes=1)
    """For simulation purposes """
    # scheduler.add_job(changeParkingDispo, 'interval', minutes=1)
    """"""
    scheduler.start()
