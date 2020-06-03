import os

import dateutil
import requests
import random
import pandas as pd
import numpy as np


class Object(object):
    pass


overpass_url = "http://overpass-api.de/api/interpreter"


# coords = [] coords.append((lon, lat))
# elif 'center' in element:
#     lon = element['center']['lon']
#     lat = element['center']['lat']
#     coords.append((lon, lat))  # Convert coordinates into numpy array
#
def fillEquipementTable():
    equipements = [
        {
            "idEquipement": 1,
            "designation": "Ouvert 24/7",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 2,
            "designation": "Vidéo surveillance",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 3,
            "designation": "Système anti incendie",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 4,
            "designation": "Couvert",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 5,
            "designation": "Ascenseur",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 6,
            "designation": "Accés PMR",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 7,
            "designation": "Ouvert 24/7",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"
        },
        {
            "idEquipement": 8,
            "designation": "Affichage LED",
            "iconUrl": "https://image.flaticon.com/icons/png/512/68/68544.png"

        }
    ]
    for equip in equipements:
        e = Equipement(equip['idEquipement'], equip['designation'], equip['iconUrl'])
        e.save()


def fillTermeTable():
    termes = [
        {
            "idTerme": 1,
            "contenu": "Terme 1"
        },
        {
            "idTerme": 2,
            "contenu": "Terme 2"
        }
    ]
    for terme in termes:
        t = Terme(terme["idTerme"], terme["contenu"])
        t.save()


def createEtagesForParking(lastCreated, nb_etages, nb_places):
    nb_places_etage = nb_places // nb_etages
    array_nb_places = [nb_places_etage] * nb_etages
    if not ((nb_places / nb_etages).is_integer()):
        array_nb_places[nb_etages - 1] += nb_places % nb_etages
    etages_ids = [idParking + 1 for idParking in range(lastCreated, lastCreated + nb_etages)]
    for index, idParking in enumerate(range(lastCreated, lastCreated + nb_etages)):
        # print("etage " + str(idParking + 1) + "nb places : " + str(array_nb_places[index]))
        etage = Etage(idParking + 1, array_nb_places[index])
        etage.save()
    return etages_ids


def createHoraireForParking(lastCreated):
    ouverture = dateutil.parser.parse("1900-01-01T07:00:00.000Z")
    fermeture = dateutil.parser.parse("1900-01-01T19:00:00.000Z")
    h = Horaire(lastCreated + 1, 1, ouverture, fermeture)
    h.save()
    return lastCreated + 1


def createTarifsForParking(lastCreated, nb_tarifs):
    tarifs = [
        {
            "duree": 60.0,
            "prix": 100.0
        },
        {
            "duree": 120,
            "prix": 150
        },
        {
            "duree": 180,
            "prix": 180
        }
    ]
    array = [1, 2, 3]
    random.shuffle(array)
    random_tarifs = array[:nb_tarifs]
    created_tarifs = [0] * nb_tarifs
    for index, tarif in enumerate(random_tarifs):
        created_tarifs[index] = lastCreated + 1 + index
        t = Tarif(lastCreated + 1 + index, tarifs[tarif - 1]["duree"], tarifs[tarif - 1]["prix"])
        t.save()
    return created_tarifs


def fillPaiementTable():
    paiementTypes = [
        {
            "idPaiment": 1,
            "type": "CIB",
            "iconUrl": "https://cdn1.iconfinder.com/data/icons/ios-11-glyphs/30/money_bag-512.png"
        },
        {
            "idPaiment": 2,
            "type": "Edahbiya",
            "iconUrl": "https://cdn1.iconfinder.com/data/icons/ios-11-glyphs/30/money_bag-512.png"

        },
        {
            "idPaiment": 3,
            "type": "Espèce",
            "iconUrl": "https://cdn1.iconfinder.com/data/icons/ios-11-glyphs/30/money_bag-512.png"
        }

    ]
    for paiement in paiementTypes:
        p = Paiment(paiement["idPaiment"], paiement["type"], paiement["iconUrl"])
        p.save()


def randomArray(max_size):
    array = [index for index in range(1, max_size + 1)]
    random.shuffle(array)
    return array[:random.randrange(1, max_size + 1)]


def fillParkingTable():
    overpass_query = """
    [out:json];
    node["amenity"="parking"](36.5461,2.8503,36.8758,3.5479);
    out center;
    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    data = response.json()
    # print(data['elements'][0])
    lastCreatedE = 0  # nbEtages
    lastCreatedH = 0  # lastCreatedHoraire
    lastCreatedT = 0  # lastCreatedTarif
    for element in data['elements'][:100]:
        if element["type"] == "node":
            lon = element['lon']
            lat = element['lat']
            id_parking = element['id']
            nb_etages = random.randrange(1, 4)
            nb_places = random.randrange(10, 50)
            nb_places_disponible = 10
            etages_ids = createEtagesForParking(lastCreatedE, nb_etages, nb_places)  # [1, 2...]
            created_horaire = createHoraireForParking(lastCreatedH)  # 1
            nb_tarifs = random.randrange(1, 4)
            created_tarifs = createTarifsForParking(lastCreatedT, nb_tarifs)
            lastCreatedE += nb_etages
            lastCreatedH += 1
            lastCreatedT += nb_tarifs
            available_equipements = randomArray(8)  # equipement de 1  a 8 ids
            available_paiements = randomArray(3)  # paiement types de 1  a 3 ids
            name = "Parking name" + str(id_parking)
            element_tag = element['tags']
            obj = Object()
            obj.__dict__ = element_tag
            if hasattr(obj, 'name'):
                name = getattr(obj, 'name')
            if nb_places != 10:
                nb_places_disponible = random.randrange(10, nb_places)
            p = Parking(id_parking, nb_etages, nb_places, nb_places_disponible, name,
                        "38, rue Guynemer. Code postal: 75006. Ville: Paris. Pays: France. M",
                        "https://cdn.static01.nicematin.com/media/npo/1440w/2012/07/image-men11q206_tj_projet-parking-sablette-small.jpg",
                        lat, lon, [created_horaire], [*etages_ids], [*created_tarifs], [*available_equipements],
                        [*available_paiements],
                        [1, 2])
            p.save()


def randomFromArray(array):
    random.shuffle(array)
    return array[:random.randrange(1, 10)]  # max 10 fav parkings


def fillUserTable():
    overpass_query_users = """
    [out:json];
    node["amenity"="pharmacy"](36.5461,2.8503,36.8758,3.5479);
    out center;
    """
    response_users = requests.get(overpass_url,
                                  params={'data': overpass_query_users})
    data = response_users.json()
    for element in data['elements'][2:300]:
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
            parkings_list = Parking.objects.all().values_list()
            parkings_ids = pd.DataFrame.from_records(parkings_list)[0].to_list()
            favoris = randomFromArray(parkings_ids)
            au = Automobiliste(id_user, "app", "null", nom, phone_number, prenom, [lat, lon], user.id, [*favoris])
            au.save()
            # print(au.idAutomobiliste, " added")


def generateNearbyGPSPosition(r, lat, lon):  # using a uniform random distribution, r radius in meters
    meters_in_one_degree_equator = 111300.0
    u = np.random.uniform(low=0, high=1)
    v = np.random.uniform(low=0, high=1)
    w = r / meters_in_one_degree_equator * np.sqrt(u)
    t = 2 * np.pi * v
    x = w * np.cos(t) # what ? att ndiro kima ana nhb ndir hh
    y = w * np.sin(t)
    print("heeeeerr", str(lon)+" "+str(lat)) # babe look pleaz
    # look cos mahoch yredj3 float d9i9a ni n9olek hadja, plz look yradje3 nd array not float
    return [lat + x / np.cos(lon), lon + y]  # itried float mais same thing att dok nhws dikika ff hh
    # wait hamlik raho khlas so wehc habiti t9oli ? wch ah? hadmoulah et toi,?lol
# kotlk wch rahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh
# rah mlih lol
# islam testit haka b str? not yet

# write her u waa say somehing ? ni nhws ki nkml nhws nji oki nsiyi this bidma
# ouii ?i dir print te3 lon and lok kunt nktb couptini chft lol sorry chft bli not my fault thb jwb ghhhh
# lmofid kotlk


def main():
    print("main")
    # fillPaiementTable()
    # fillTermeTable()
    # fillEquipementTable()
    # fillParkingTable()
    # fillUserTable()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    from myparking_api.models import Parking, Automobiliste, User, Equipement, Etage, Horaire, Terme, Tarif, Paiment

    main()
