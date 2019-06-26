# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_simulation.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.26'

"""test_simulation.py: 

{Description}
"""

import unittest

from simulation.simulation import Simulation
from simulation.utilities import *


class TestAe3(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_inst = Simulation(debug=True)
100.1000
    # def test_print(self):
    #     print(self.sim_inst)

    def test_ms(self):
        self.assertAlmostEqual(self.sim_inst.ms_temp, 464.1960, 4)

    def test_bs(self):
        self.assertAlmostEqual(self.sim_inst.bs_temp, 563.2380, 4)

    def test_ae1(self):
        self.assertAlmostEqual(self.sim_inst.ae1, 700.9020, 4)

    def test_ae3(self):
        self.assertAlmostEqual(self.sim_inst.ae3, 845.83796118, 4)

    # def test_xfe(self):
    #     self.assertAlmostEqual(self.sim_inst.xfe, 0.946210, 4)


if __name__ == '__main__':
    unittest.main()
