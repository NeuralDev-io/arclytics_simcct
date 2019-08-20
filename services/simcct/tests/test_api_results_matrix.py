# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_results_matrix.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__date__ = '2019.08.20'
"""test_api_results_matrix.py: 

Unit testing the ResultsMatrix wrapper type created around a numpy.zeros()
ndarray. 
"""

import unittest
from simulation.results import ResultsMatrix


class MyTestCase(unittest.TestCase):
    def test_init(self):
        mat = ResultsMatrix(rows=10)
        self.assertEqual(mat.shape, (10, 2))
        self.assertEqual(mat[0, 0], 0.0)
        self.assertEqual(mat[0, 1], 0.0)
        self.assertEqual(mat[9, 1], 0.0)
        self.assertEqual(mat[9, 1], 0.0)

    def test_override_braces_set_item(self):
        mat = ResultsMatrix(rows=10)
        mat[0, 0] = 10.0
        mat[9, 1] = 92
        self.assertEqual(mat[0, 0], 10.0)
        self.assertEqual(mat[9, 1], 92)

    def test_trim_zeros(self):
        mat = ResultsMatrix(rows=10)
        mat[0, 0] = 10.0
        mat[0, 1] = 30.0
        mat[1, 0] = 20.0
        mat[1, 1] = 40.0
        mat[2, 1] = 50.0
        time, temp = mat.trim_zeros()
        self.assertEqual(time.shape, (2, ))
        self.assertEqual(temp.shape, (3, ))

    def test_override_braces_get_item(self):
        mat = ResultsMatrix(rows=10)
        mat[0, 0] = 10.0
        mat[0, 1] = 10.0
        self.assertEqual(mat[0][0], 10.0)
        self.assertEqual(mat[0][1], 10.0)

    def test_to_dict(self):
        mat = ResultsMatrix(rows=10)
        mat[0, 0] = 10.0
        mat[0, 1] = 10.0
        mat_dict = mat.to_dict()
        self.assertEqual(mat_dict['temp'][0], 10.0)
        self.assertEqual(mat_dict['time'][0], 10.0)

    def test_append(self):
        mat = ResultsMatrix(rows=2)
        mat.append(0, 1.0, 2.0)
        self.assertEqual(mat[0, 0], 1.0)
        self.assertEqual(mat[0, 1], 2.0)

    def test_multiple_resizes(self):
        mat = ResultsMatrix(rows=2)
        mat[0, 0] = 1.0
        mat[1, 0] = 2.0  # resize
        self.assertEqual(mat.rows, 4)
        self.assertEqual(mat.shape, (4, 2))
        mat[2, 0] = 3.0
        mat[3, 0] = 4.0  # resize
        self.assertEqual(mat.rows, 8)
        self.assertEqual(mat.shape, (8, 2))
        mat[6, 0] = 5.0  # resize
        self.assertEqual(mat.rows, 16)
        self.assertEqual(mat.shape, (16, 2))
        mat[33, 0] = 99.9
        self.assertEqual(mat[32, 0], 0.0)
        self.assertEqual(mat.rows, 66)
        self.assertEqual(mat.shape, (66, 2))
        mat[244, 0] = 88.8
        self.assertEqual(mat.rows, 488)
        self.assertEqual(mat.shape, (488, 2))
        self.assertEqual(mat[233, 0], 0.0)


if __name__ == '__main__':
    unittest.main()
