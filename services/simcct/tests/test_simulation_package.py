# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_simulation_package.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__status__ = 'development'
__date__ = '2019.06.26'

import os
import sys
import unittest

from simulation.phasesimulation import *

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(BASE_DIR)


class TestConfigurations(unittest.TestCase):
    def setUp(self) -> None:
        self.configs = SimConfiguration(debug=True)

    def test_configurations(self):
        pass


class TestUserCoolingCurve(unittest.TestCase):
    def test_user_cooling_result(self):
        pass


class TestTTT(unittest.TestCase):
    def test_ttt_result(self):
        pass


class TestCCT(unittest.TestCase):
    def test_cct_result(self):
        pass


if __name__ == '__main__':
    unittest.main()
