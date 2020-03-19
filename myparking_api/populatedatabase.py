import os

import requests
import random


class Object(object):
    pass


overpass_url = "http://overpass-api.de/api/interpreter"


# coords = [] coords.append((lon, lat))
# elif 'center' in element:
#     lon = element['center']['lon']
#     lat = element['center']['lat']
#     coords.append((lon, lat))  # Convert coordinates into numpy array

def fillParkingTable():
    overpass_query = """
    [out:json];
    node["amenity"="parking"](36.5461,2.8503,36.8758,3.5479);
    out center;
    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    data = response.json()

    for element in data['elements'][100]:
        if element['type'] == 'node':
            lon = element['lon']
            lat = element['lat']
            id_parking = element['id']
            nb_etages = random.randrange(1, 5)
            nb_places = random.randrange(10, 20)
            nb_places_disponible = 10
            name = "Parking name" + str(id_parking)
            element_tag = element['tags']
            obj = Object()
            obj.__dict__ = element_tag
            if hasattr(obj, 'name'):
                name = getattr(obj, 'name')
            if nb_places != 10:
                nb_places_disponible = random.randrange(10, nb_places)
            p = Parking(id_parking, nb_etages, nb_places, name,
                        "38, rue Guynemer. Code postal: 75006. Ville: Paris. Pays: France. M",
                        "https://cdn.static01.nicematin.com/media/npo/1440w/2012/07/image-men11q206_tj_projet-parking-sablette-small.jpg",
                        lat, lon, [1, 2], [1], [1], [1], [1], [1, 2])
            p.save()


def fillUserTable():
    overpass_query_users = """
    [out:json];
    node["amenity"="pharmacy"](36.5461,2.8503,36.8758,3.5479);
    out center;
    """
    response_users = requests.get(overpass_url,
                                  params={'data': overpass_query_users})
    data = response_users.json()
    for element in data['elements'][:300]:
        if element['type'] == 'node':
            lon = element['lon']
            lat = element['lat']
            id_user = element['id']
            user_name = "username" + str(element['id'])
            nom = "nom" + str(element['id'])
            prenom = "prenom" + str(element['id'])
            email_user = str(element['id']) + 'a@esi.dz'
            password_user = str(element['id']) + 'password'
            phone_number = str(element['id'])
            user = User.objects.create_user(user_name, email_user, password_user)
            au = Automobiliste(id_user, "app", "null", nom, phone_number, prenom, user.id, [1], lat, lon)
            au.save()
            print(au.idAutomobiliste, " added")


def main():
    print("main")
    # fillParkingTable()
    # fillUserTable()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, Automobiliste, User

    main()
