import os
import unittest
from unittest.mock import patch

import django
import pandas as pd
from django.conf import settings
from django.core.wsgi import get_wsgi_application
# from model_optim.optimization import NP, NU

from model_optim.helpers.calculateCentroid import get_centermost_point
from model_optim.helpers.calculateDistance import calculateDistance
from model_optim.optimization import SommeDist, F, TauxDisp

dataframe = pd.DataFrame(
    data={'NB_PLACES_LIBRES': [1, 2], 'NB_PLACES': [2, 4], 'LAG': [0, 1], 'LON': [1, 0], 'LAT': [0, 1]})
distance_matrix = [[1, 2],
                   [3, 4],
                   [5, 6]]


class TestOptimizationMethods(unittest.TestCase):

    def test_somme_distance(self):
        self.assertEqual(SommeDist(distance_matrix, 0), 0)

    # def test_fonction_cout(self):
    #     self.assertEqual(F(dataframe, distance_matrix, 0, 0), (0.5 * 1 / 3 + 0.5 * (1 - 1 / 2)) ** 2)

    def test_taux_disponiblite(self):
        self.assertEqual(TauxDisp(dataframe, 0), 1 / 2)

    def test_calculate_centroid(self):
        cluster = dataframe[['LAG', 'LON']].to_numpy()
        self.assertEqual(get_centermost_point(cluster), tuple([1, 0]))

    def test_calculate_distance_zero(self):
        self.assertEqual(calculateDistance(dataframe, 0).tolist(), [[0.0, 0.0], [0.0, 0.0]])

    def test_calculate_distance_non_zero(self):
        self.assertEqual(calculateDistance(dataframe, 2).tolist(), [[0.0, 314.4991969480804], [314.4991969480804, 0.0]])


if __name__ == '__main__':
    unittest.main()
