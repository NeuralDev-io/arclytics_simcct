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
import numpy as np
from simulation.simconfiguration import SimConfiguration
from simulation.ae3_utilities import *
from simulation.simulations import *


class BaseConfigurationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_inst = SimConfiguration(debug=True)

    @classmethod
    def setUpClass(cls) -> None:
        # This runs only once
        super(BaseConfigurationTest, cls).setUpClass()


class TestMSnBS(BaseConfigurationTest):
    def setUp(self) -> None:
        super(TestMSnBS, self).setUp()

    def test_ms(self):
        self.assertAlmostEqual(self.sim_inst.ms_temp, 464.1960, 4)

    def test_bs(self):
        self.assertAlmostEqual(self.sim_inst.bs_temp, 563.2380, 4)


class TestAe1nAe3(BaseConfigurationTest):
    def setUp(self) -> None:
        super(TestAe1nAe3, self).setUp()

        # Set up some instance variables for other tests
        self.wt = self.sim_inst.comp_parent.copy()
        self.temp = np.float64(0.0)
        self.a_vect = None
        self.x_vect = None
        self.ai_vect = None
        self.t0 = None
        self.b_mat = None
        self.e_mat = None
        self.g_c = None
        self.c_f = None
        self.h = None
        self.g = None
        self.gi = None

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
        self.c_f = c_af / total_af

        # Mole fraction of each element (excluding Carbon and Iron)
        self.x_vect[1:-1] = self.x_vect[1:-1] / total_af

        self.t0 = tzero2(self.wt_c)

        self.assertAlmostEqual(self.t0, 1160.13050698808, 8)

    def test_dg_dh_fit(self):
        self.test_con_wt_2_mol()
        self.test_tzero2()

        # This will test only the first loop in the while loop

        self.temp = self.t0  # starting point for evaluation
        self.a_vect = np.zeros(20, dtype=np.float64)
        z = np.float64(1.0)
        ctr = 0
        self.g_c = np.float64(0.0)
        self.g = np.float64(0.0)
        self.h = np.float64(0.0)

        # Run it just once
        # while z > 0.5:
        if self.temp > 0:
            self.g, self.temp = dg_fit(self.g, self.temp)
        else:
            logger.error("Negative temperature determined for Ae3.")
        self.assertAlmostEqual(self.g, 3.980423951788, 8)
        self.assertAlmostEqual(self.temp, 1160.1305069880798, 8)

        self.g_c = -15323 + 7.686 * self.temp
        self.assertAlmostEqual(self.g_c, -6406.2369232896181, 8)

        if self.temp > 1183:
            self.h = 2549.0 - 2.746 * self.temp + 0.0006503 * math.pow(self.temp, 2)
            self.g = 2476.0 - 5.03 * self.temp + 0.003363 * math.pow(self.temp, 2) - 0.000000744 \
                * math.pow(self.temp, 3)
        else:
            self.h, self.temp = dh_fit(self.temp)

        # logger.info("g: {},\n h: {},\n temp: {}".format(g, h, temp))
        self.assertAlmostEqual(self.h, 237.83686626490027, 10)
        self.assertAlmostEqual(self.temp, 1160.1305069880798, 10)

    def test_eta2li96(self):
        # TODO: Need to test some values in this, but can be done later
        np.set_printoptions(precision=4)
        self.b_mat = eta2li96()
        # logger.pprint(self.b_mat)

    def test_dgi22(self):
        self.e_mat = dgi22()
        # logger.pprint(self.e_mat)

    def test_ai_eqn3(self):
        self.test_con_wt_2_mol()
        self.test_tzero2()
        self.test_dg_dh_fit()

        _sum = np.float64(0.0)
        delta_t = np.float64(0.0)

        self.test_eta2li96()
        self.test_dgi22()

        # This will only test the first loop

        self.ai_vect = np.zeros(self.sim_inst.comp_parent.shape[0], dtype=np.float128)
        gi = None
        e_aust1i, e_aust11 = None, None  # UP's
        e_alpha1i, e_alpha11 = None, None  # DOWN's

        for m in range(1, 3):
            if self.x_vect[m] == 0:
                self.a_vect[m] = 0.0
                self.ai_vect[m] = 1.0
            else:
                e_aust1i = np.float64(self.b_mat[m, 4] + self.b_mat[m, 5] / self.temp)
                e_aust11 = np.float64(8910 / self.temp)  # Bhadeshia code

                if m == 1:
                    self.gi = 6.118 * self.temp - 7808.0  # special set for Mn
                else:
                    self.gi = self.e_mat[m, 1] + (self.e_mat[m, 2] + self.e_mat[m, 3] * self.temp + self.e_mat[m, 4] *
                                             math.log(self.temp)) * self.temp

                H1 = np.float64(-15319.0)

                e_alpha1i = self.b_mat[m, 1] + self.b_mat[m, 2] / self.temp
                e_alpha11 = 4.786 + 5066 / self.temp

                self.ai_vect[m] = ai_eqn3(
                    t0=self.t0, dg_n=self.gi, dg_c=self.g_c, dg_fe=self.g, dh_c=H1, dh_fe=self.h,
                    eta1n_up=e_aust1i, eta11_up=e_aust11, eta1n_down=e_alpha1i, eta11_down=e_alpha11,
                    x1_up=self.c_f, x1_down=self.c_f
                )

                _sum = _sum + self.x_vect[m] * self.ai_vect[m]

                self.assertAlmostEqual(self.t0, 1160.1305069880798, 10)
                self.assertAlmostEqual(self.h, 237.83686626490027, 10)
                self.assertAlmostEqual(self.temp, 1160.1305069880798, 10)
                if m == 1:
                    self.assertAlmostEqual(e_alpha11, 9.1527500936, 10)
                    self.assertAlmostEqual(e_alpha1i, -3.8363782505, 10)
                    self.assertAlmostEqual(e_aust11, 7.6801704173, 10)
                    self.assertAlmostEqual(e_aust1i, -4.14694723655, 10)
                    self.assertAlmostEqual(self.x_vect[m], 0.017523547399, 10)
                    # TODO: Why can't I seem to get the 8th degree
                    self.assertAlmostEqual(self.ai_vect[m], -0.0011124401207938273, 7)
                    self.assertAlmostEqual(_sum, -1.9493897185882612E-05, 8)

    def test_ae3(self):
        # logger.info("Ae3: {:.4f}".format(self.sim_inst.ae3))
        self.assertAlmostEqual(self.sim_inst.ae3, 845.83796118, 4)


class TestXfe(BaseConfigurationTest):
    def setUp(self) -> None:
        super(TestXfe, self).setUp()
        self.results_mat = None

    def test_ae3_multi_carbon(self):
        # Do 2 iterations of the for loop and check the results for results[0:1, 0:5]
        self.results_mat = np.zeros((1000, 22), dtype=np.float64)
        pass

    def test_ceut(self):
        self.test_ae3_multi_carbon()
        # Test the XfeMethod2 section where self.ceut is changed.
        pass

    def test_xfe(self):
        logger.info("Xfe: {}, Ceut: {}. Cf: {}".format(self.sim_inst.xfe, self.sim_inst.ceut, self.sim_inst.cf))
        self.assertAlmostEqual(self.sim_inst.xfe, 0.94621026894865523, 8)


class TestSimulation(unittest.TestCase):
    def setUp(self):
        sim_inst = SimConfiguration(debug=True)
        self.simulation = Simulation(sim_inst)
        self.simulation.ttt()
        logger.info(self.simulation)

    # def test__sigmoid2(self):
    #     self.assertAlmostEqual(, 1.31950870247819, 8)


class TestCoolingCurveTemperature(BaseConfigurationTest):
    def setUp(self) -> None:
        self.simulation = Simulation(self.sim_inst)

    def test_ccr(self):

        pass


if __name__ == '__main__':
    unittest.main()
