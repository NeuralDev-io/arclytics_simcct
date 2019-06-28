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
from pprint import pprint
import numpy as np
from simulation.simconfiguration import SimConfiguration
from simulation.ae3_utilities import *


class BaseSimulationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_inst = SimConfiguration(debug=True)

    # def test_print(self):
    #     print(self.sim_inst)


class TestMSnBS(BaseSimulationTest):
    def setUp(self) -> None:
        super(TestMSnBS, self).setUp()

    def test_ms(self):
        self.assertAlmostEqual(self.sim_inst.ms_temp, 464.1960, 4)

    def test_bs(self):
        self.assertAlmostEqual(self.sim_inst.bs_temp, 563.2380, 4)


class TestAe3(BaseSimulationTest):
    def setUp(self) -> None:
        super(TestAe3, self).setUp()

        # Set up some instance variables for other tests
        self.wt = self.sim_inst.comp_parent.copy()
        self.x_vect = None
        self.t0 = None
        self.b_mat = None
        self.e_mat = None

    def test_ae1(self):
        self.assertAlmostEqual(self.sim_inst.ae1, 700.9020, 4)

    def test_con_wt_2_mol(self):
        wt = self.sim_inst.comp_parent.copy()
        wt['weight'][wt['name'] == 'carbon'] = 0.0
        wt['weight'][wt['name'] == 'iron'] = 0.0
        self.assertAlmostEqual(wt['weight'][wt['name'] == 'carbon'], 0.0, 6)
        self.assertAlmostEqual(wt['weight'][wt['name'] == 'iron'], 0.0, 6)

        self.wt_pc = np.sum(wt['weight'], dtype=np.float64).astype(np.float64).item()
        self.assertAlmostEqual(self.wt_pc, 2.21, 2)

        self.wt_c = self.sim_inst.comp_parent['weight'][self.sim_inst.comp_parent['name'] == 'carbon'][0]
        self.wt_pc = self.wt_pc + self.wt_c
        self.assertAlmostEqual(self.wt_pc, 2.254, 3)

        wt['weight'][wt['name'] == 'iron'] = 100 - self.wt_pc
        wt['weight'][wt['name'] == 'carbon'] = self.wt_c

        self.x_vect, yy_vect = convert_wt_2_mol(wt)

        self.assertAlmostEqual(self.x_vect[0], 0.00203854362, 8)
        self.assertAlmostEqual(self.x_vect[1], 0.01752354739, 8)
        self.assertAlmostEqual(self.x_vect[2], 0.00435848465, 8)
        self.assertAlmostEqual(self.x_vect[5], 0.00150812803, 8)
        self.assertAlmostEqual(self.x_vect[18], 0.97457129628, 8)

        self.assertAlmostEqual(yy_vect[0], 0.0020917337045811, 8)
        self.assertAlmostEqual(yy_vect[1], 0.0179807752048335, 8)
        self.assertAlmostEqual(yy_vect[2], 0.00447220708305018, 8)
        self.assertAlmostEqual(yy_vect[2], 0.00447220708305018, 8)
        self.assertAlmostEqual(yy_vect[5], 0.00154747840555407, 8)

    def test_tzero2(self):
        # Must run the previous test to update the needed variables
        self.test_con_wt_2_mol()

        fe_af = self.x_vect[-1]  # moles Fe
        c_af = self.x_vect[0]  # moles C
        other_e_sum_af = np.sum(self.x_vect[1:-1], dtype=np.float64).astype(np.float64).item()
        total_af = fe_af + c_af + other_e_sum_af
        cf = c_af / total_af

        # Mole fraction of each element (excluding Carbon and Iron)
        self.x_vect[1:-1] = self.x_vect[1:-1] / total_af

        self.t0 = tzero2(self.wt_c)

        self.assertAlmostEqual(self.t0, 1160.13050698808)

    def test_dg_dh_fit(self):
        self.test_con_wt_2_mol()
        self.test_tzero2()

        temp = self.t0  # starting point for evaluation
        a_vect = np.zeros(20, dtype=np.float64)
        z = np.float64(1.0)
        ctr = 0
        g_c = np.float64(0.0)
        g = np.float64(0.0)
        h = np.float64(0.0)

        # Run it just once
        # while z > 0.5:
        if temp > 0:
            g, temp = dg_fit(g, temp)
        else:
            logger.error("Negative temperature determined for Ae3.")
        self.assertAlmostEqual(g, 3.980423951788, 8)
        self.assertAlmostEqual(temp, 1160.1305069880798, 8)

        g_c = -15323 + 7.686 * temp
        self.assertAlmostEqual(g_c, -6406.2369232896181, 8)

        if temp > 1183:
            h = 2549.0 - 2.746 * temp + 0.0006503 * math.pow(temp, 2)
            g = 2476.0 - 5.03 * temp + 0.003363 * math.pow(temp, 2) - 0.000000744 * math.pow(temp, 3)
        else:
            h, temp = dh_fit(temp)

        # logger.info("g: {},\n h: {},\n temp: {}".format(g, h, temp))
        self.assertAlmostEqual(h, 237.83686626490027, 8)

    def test_eta2li96(self):
        # TODO: Need to test some values in this, but can be done later
        np.set_printoptions(precision=4)
        self.b_mat = eta2li96()
        # logger.pprint(self.b_mat)

    def test_dgi22(self):
        self.e_mat = dgi22()
        # logger.pprint(self.e_mat)

    def test_ai_eqn3(self):
        
        pass

    # def test_ae3(self):
    #     self.assertAlmostEqual(self.sim_inst.ae3, 845.83796118, 4)

    # def test_xfe(self):
    #     self.assertAlmostEqual(self.sim_inst.xfe, 0.946210, 4)


if __name__ == '__main__':
    unittest.main()
