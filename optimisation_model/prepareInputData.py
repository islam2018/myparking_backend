import os
import random

import requests
import json


class Object(object):
    pass


HERE_API_KEY = "SnEjiUueUMbL4zeFjvfi6vx4JMWGkdCrof7QDZLQWoY"
arrayStarts = []
arrayDestinations = []
arrayNbPlaces = []
arrayNbPlacesLibre = []
objectStarts = Object()
objectDestinations = Object()


def fillMatrix(array, indexStartUsers, indexEndUsers, indexStartParkings, indexEndParings):
    for index, item in enumerate(arrayStarts[indexStartUsers:indexEndUsers]):
        setattr(objectStarts, 'start' + str(index), item)

    for index, item in enumerate(arrayDestinations[indexStartParkings:indexEndParings]):
        setattr(objectDestinations, 'destination' + str(index), item)
    travelResponse = requests.get("https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json",
                                  params={
                                      'apiKey': HERE_API_KEY,
                                      **objectStarts.__dict__,
                                      **objectDestinations.__dict__,
                                      'mode': 'balanced;car;traffic:enabled',
                                      'summaryAttributes': 'traveltime,distance'
                                  })

    json_travel_data = json.loads(travelResponse.text)
    matrix = json_travel_data['response']['matrixEntry']
    for i in matrix:
        array[i['startIndex']][i['destinationIndex']] = i['summary']['distance']


def getDistanceMatrix(NU, NP):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, Automobiliste

    drivers = Automobiliste.objects.all()[0:NU]
    for row in drivers:
        arrayStarts.append(str(row.lattitude) + ',' + str(row.longitude))

    parkings = Parking.objects.all()[0:NP]
    for row in parkings:
        arrayDestinations.append(str(row.lattitude) + ',' + str(row.longitude))
        arrayNbPlaces.append(row.nbPlaces)
        arrayNbPlacesLibre.append(random.randrange(10, row.nbPlaces + 1))

    k, modK = divmod(arrayDestinations.__len__(), 100)  # limite destinations here 100
    m, modM = divmod(arrayStarts.__len__(), 15)  # limite start here 15
    # add modulo later
    array = [[None] * NP] * NU
    for x in range(k + 1):
        for y in range(m + 1):
            addK = 100
            addM = 15
            if x == k:
                addK = modK
            if y == m:
                addM = modM
            print(y * 15, y * 15 + addM, x * 100, x * 100 + addK)
            fillMatrix(array, y * 15, y * 15 + addM, x * 100, x * 100 + addK)

    return array, arrayNbPlaces, arrayNbPlacesLibre


# def main():
#     array, arrayNbPlaces, arrayNbPlacesLibre = getDistanceMatrix(4, 2)
#     print(array)
#     print(arrayNbPlaces)
#     print(arrayNbPlacesLibre)
#
#
# if __name__ == '__main__':
#     main()
