# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Arvy Salazar <@Xaraox>, Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.26'
"""test_simulation.py: 

The test module for the Phase Simulation package.
"""

import os
import sys
import unittest

from simulation.ae3_utilities import *
from simulation.phasesimulation import *

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(BASE_DIR)


class TestSimulation(unittest.TestCase):
    def setUp(self) -> None:
        self.configs = SimConfiguration(debug=True)

    def test_configurations(self):
        pass

    def test_ttt_result(self):
        pass

    def test_cct_result(self):
        pass


if __name__ == '__main__':
    unittest.main()
