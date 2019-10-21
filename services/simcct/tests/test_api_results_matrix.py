# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_results_matrix.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__date__ = '2019.08.20'

import unittest

from simulation.dynamic_ndarray import DynamicNdarray


class MyTestCase(unittest.TestCase):
    def test_init(self):
        mat = DynamicNdarray(shape=(10, 2))
        self.assertEqual(mat.shape, (10, 2))
        self.assertEqual(mat[0, 0], 0.0)
        self.assertEqual(mat[0, 1], 0.0)
        self.assertEqual(mat[9, 1], 0.0)
        self.assertEqual(mat[9, 1], 0.0)

    def test_override_braces_set_item(self):
        mat = DynamicNdarray(shape=(10, 2))
        mat[0, 0] = 10.0
        mat[9, 1] = 92
        self.assertEqual(mat[0, 0], 10.0)
        self.assertEqual(mat[9, 1], 92)

    def test_trim(self):
        mat = DynamicNdarray(shape=(10, 2))
        mat[0, 0] = 10.0
        mat[0, 1] = 30.0
        mat[1, 0] = 20.0
        mat[1, 1] = 40.0
        mat[2, 1] = 50.0
        # Trimming using traditional numpy. Remember it returns the internal
        # ndarray as the object now.
        mat = mat[:4, :]
        self.assertEqual(mat.shape, (4, 2))

    def test_override_braces_get_item(self):
        mat = DynamicNdarray(shape=(10, 2))
        mat[0, 0] = 10.0
        mat[0, 1] = 10.0
        self.assertEqual(mat[0][0], 10.0)
        self.assertEqual(mat[0][1], 10.0)

    def test_resize_down_fail(self):
        mat = DynamicNdarray(shape=(100, 2))
        with self.assertRaises(Exception) as context:
            mat.resize(50)
        self.assertEqual(mat.shape, (100, 2))

    def test_multiple_resizes(self):
        mat = DynamicNdarray(shape=(2, 2))
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
