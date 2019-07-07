# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_simulation.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Arvy Salazar <@Xaraox>, Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
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

import unittest

from ae3_utilities import *
from phasesimulation import *


class BaseConfigurationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_inst = SimConfiguration(debug=True)

    # @classmethod
    # def setUpClass(cls) -> None:
    #     This runs only once
    # super(BaseConfigurationTest, cls).setUpClass()


class TestMSnBS(BaseConfigurationTest):
    def setUp(self) -> None:
        super(TestMSnBS, self).setUp()

    def test_ms(self):
        self.assertAlmostEqual(self.sim_inst.ms_temp, 464.19600000000008, 10)

    def test_bs(self):
        self.assertAlmostEqual(self.sim_inst.bs_temp, 563.23800000000006, 10)


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
        self.assertAlmostEqual(self.sim_inst.ae1, 700.90196296296301, 10)

    def test_con_wt_2_mol(self):
        wt = self.sim_inst.comp_parent.copy()
        wt['weight'][wt['name'] == 'carbon'] = 0.0
        wt['weight'][wt['name'] == 'iron'] = 0.0
        self.assertAlmostEqual(wt['weight'][wt['name'] == 'carbon'], 0.0, 6)
        self.assertAlmostEqual(wt['weight'][wt['name'] == 'iron'], 0.0, 6)

        self.wt_pc = np.sum(wt['weight'],
                            dtype=np.float64).astype(np.float64).item()
        self.assertAlmostEqual(self.wt_pc, 2.21, 2)

        self.wt_c = self.sim_inst.comp_parent['weight'][
            self.sim_inst.comp_parent['name'] == 'carbon'][0]
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
        other_e_sum_af = np.sum(self.x_vect[1:-1],
                                dtype=np.float64).astype(np.float64).item()
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
            self.h = 2549.0 - 2.746 * self.temp + 0.0006503 * math.pow(
                self.temp, 2
            )
            self.g = (
                2476.0 - 5.03 * self.temp + 0.003363 * math.pow(self.temp, 2) -
                0.000000744 * math.pow(self.temp, 3)
            )
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

        self.test_eta2li96()
        self.test_dgi22()

        # This will only test the first loop

        self.ai_vect = np.zeros(
            self.sim_inst.comp_parent.shape[0], dtype=np.float64
        )

        for m in range(1, 3):
            if self.x_vect[m] == 0:
                self.a_vect[m] = 0.0
                self.ai_vect[m] = 1.0
            else:
                e_aust1i = np.float64(
                    self.b_mat[m, 4] + self.b_mat[m, 5] / self.temp
                )
                e_aust11 = np.float64(8910 / self.temp)  # Bhadeshia code

                if m == 1:
                    self.gi = 6.118 * self.temp - 7808.0  # special set for Mn
                else:
                    self.gi = self.e_mat[m, 1] + (
                        self.e_mat[m, 2] + self.e_mat[m, 3] * self.temp +
                        self.e_mat[m, 4] * math.log(self.temp)
                    ) * self.temp

                h1 = np.float64(-15319.0)

                e_alpha1i = self.b_mat[m, 1] + self.b_mat[m, 2] / self.temp
                e_alpha11 = 4.786 + 5066 / self.temp

                self.ai_vect[m] = ai_eqn3(
                    t0=self.t0,
                    dg_n=self.gi,
                    dg_c=self.g_c,
                    dg_fe=self.g,
                    dh_c=h1,
                    dh_fe=self.h,
                    eta1n_up=e_aust1i,
                    eta11_up=e_aust11,
                    eta1n_down=e_alpha1i,
                    eta11_down=e_alpha11,
                    x1_up=self.c_f,
                    x1_down=self.c_f
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
                    self.assertAlmostEqual(
                        self.ai_vect[m], -0.0011124401207938273, 7
                    )
                    self.assertAlmostEqual(_sum, -1.9493897185882612E-05, 8)

    def test_ae3(self):
        # logger.info("Ae3: {:.4f}".format(self.sim_inst.ae3))
        self.assertAlmostEqual(self.sim_inst.ae3, 845.83796118539999, 10)


class TestXfe(BaseConfigurationTest):
    def setUp(self) -> None:
        super(TestXfe, self).setUp()
        self.results_mat = None

    def test_ae3_multi_carbon(self):
        # Do 2 iterations of the for loop and check the results for results[0:1, 0:5]
        wt = self.sim_inst.comp_parent.copy()
        self.results_mat = np.zeros((1000, 22), dtype=np.float64)

        ae3_multi_carbon(wt, self.results_mat)

        self.assertAlmostEqual(self.results_mat[0, 0], 0, 8)
        self.assertAlmostEqual(self.results_mat[0, 1], 869.853324584521, 8)
        self.assertAlmostEqual(self.results_mat[0, 2], 910.690613312279, 8)
        self.assertAlmostEqual(self.results_mat[0, 3], -0.00111210865060011, 8)
        self.assertAlmostEqual(self.results_mat[0, 4], 0.000627505594071084, 8)
        self.assertAlmostEqual(self.results_mat[0, 5], 1, 8)

        self.assertAlmostEqual(self.results_mat[1, 0], 0.01, 8)
        self.assertAlmostEqual(self.results_mat[1, 1], 863.8233624987, 8)
        self.assertAlmostEqual(self.results_mat[1, 2], 904.97196331503, 8)
        self.assertAlmostEqual(self.results_mat[1, 3], -0.00111734265308321, 8)
        self.assertAlmostEqual(self.results_mat[1, 4], 0.00060366887082998, 8)
        self.assertAlmostEqual(self.results_mat[1, 5], 1, 8)
        pass

    def test_ceut(self):
        # Test the XfeMethod2 section where self.ceut is changed.
        self.test_ae3_multi_carbon()
        if self.sim_inst.ae1 > 0:
            for i in range(1000):
                if self.results_mat[i, 1] <= self.sim_inst.ae1:
                    self.ceut = self.results_mat[i, 0]
                    break

        self.assertAlmostEqual(self.ceut, 0.830000000000001, 15)  # fails at 16
        pass

    def test_xfe(self):
        # logger.info("Xfe: {}, Ceut: {}. Cf: {}".format(self.sim_inst.xfe, self.sim_inst.ceut, self.sim_inst.cf))
        self.assertAlmostEqual(self.sim_inst.xfe, 0.94621026894865523, 10)


class TestSimulation(BaseConfigurationTest):
    def setUp(self):
        super(TestSimulation, self).setUp()
        self.simulation = PhaseSimulation(self.sim_inst, debug=True)
        self.simulation.ttt()
        self.integrated2_mat = None

    def test_vol_phantom_frac2(self):
        # TODO remember to do the tests for Kirkaldy
        self.integrated2_mat = np.zeros((4, 11), dtype=np.float64)

        self.simulation.test_vol_phantom_frac2(self.integrated2_mat)

        if self.sim_inst.method == Method.Li98:
            # START precipitation
            self.assertAlmostEqual(
                self.integrated2_mat[2, 5], 0.00946210268948655, 10
            )  # xf
            self.assertAlmostEqual(
                self.integrated2_mat[2, 0], 0.10097017653666272, 10
            )  # sig_int_ferrite
            self.assertAlmostEqual(
                self.integrated2_mat[2, 6], 0.18590909090909005, 10
            )  # xp
            self.assertAlmostEqual(
                self.integrated2_mat[2, 1], 0.57179585077564765, 10
            )  # sig_int_pearlite
            self.assertAlmostEqual(self.integrated2_mat[2, 7], 0.01, 10)  # xb
            self.assertAlmostEqual(
                self.integrated2_mat[2, 2], 0.10434035495645357, 10
            )  # sig_int_bainite
            # FINISH precipitation
            self.assertAlmostEqual(
                self.integrated2_mat[3, 0], 1.7683472888806175, 10
            )  # xf
            self.assertAlmostEqual(
                self.integrated2_mat[3, 1], 2.0516588406776703, 10
            )  # xp
            self.assertAlmostEqual(
                self.integrated2_mat[3, 2], 2.0253789317772588, 10
            )  # xb
        elif self.sim_inst.method == Method.Kirkaldy83:
            # START precipitation
            self.assertAlmostEqual(
                self.integrated2_mat[0, 0], 0.65227162834046781, 10
            )  # sig_int_ferrite
            self.assertAlmostEqual(
                self.integrated2_mat[0, 1], 1.5965529826649862, 10
            )  # sig_int_pearlite
            self.assertAlmostEqual(
                self.integrated2_mat[0, 2], 0.64064546121071431, 10
            )  # sig_int_bainite
            # FINISH precipitation
            self.assertAlmostEqual(
                self.integrated2_mat[1, 0], 3.2563305391378292, 10
            )
            self.assertAlmostEqual(
                self.integrated2_mat[1, 1], 1.0962795750751819, 10
            )
            self.assertAlmostEqual(
                self.integrated2_mat[1, 2], 22.091776696075449, 10
            )
        pass

    def test_torr_calc(self):
        """ Checks the first 2 values. """
        self.test_vol_phantom_frac2()

        self.simulation.test_vol_phantom_frac2(self.integrated2_mat)

        torr = 0.0

        tcurr = (round(self.sim_inst.bs_temp) - 50)

        #  Phase F start
        torr = self.simulation.test_torr_calc2(
            torr, Phase.F, tcurr, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 3.056444385041388, 10)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.F, tcurr + 1, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 3.01585390138463, 10)
        #  Phase F finish
        torr = self.simulation.test_torr_calc2(
            torr, Phase.F, tcurr, self.integrated2_mat, 2
        )
        self.assertAlmostEqual(torr, 53.529223452826173, 10)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.F, tcurr + 1, self.integrated2_mat, 2
        )
        self.assertAlmostEqual(torr, 52.818339564228445, 10)

        # Phase P start
        torr = self.simulation.test_torr_calc2(
            torr, Phase.P, tcurr, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 330.41439902451839, 10)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.P, tcurr + 1, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 328.30774976008854, 10)
        # Phase P Finish
        torr = self.simulation.test_torr_calc2(
            torr, Phase.P, tcurr, self.integrated2_mat, 2
        )
        self.assertAlmostEqual(torr, 1185.5588352491131, 10)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.P, tcurr + 1, self.integrated2_mat, 2
        )
        self.assertAlmostEqual(torr, 1177.9999738447998, 10)

        tcurr = round(self.sim_inst.ms_temp)
        # Phase B start
        torr = self.simulation.test_torr_calc2(
            torr, Phase.B, tcurr, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 0.083850562945195328, 10)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.B, tcurr + 1, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 0.0834184750169105, 10)
        # Phase finish
        torr = self.simulation.test_torr_calc2(
            torr, Phase.B, tcurr, self.integrated2_mat, 2
        )
        self.assertAlmostEqual(torr, 1.6276460213092019, 10)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.B, tcurr + 1, self.integrated2_mat, 2
        )
        self.assertAlmostEqual(torr, 1.6192586453319149, 10)
        # Phase M
        tcurr = round(self.sim_inst.ms_temp)
        torr = self.simulation.test_torr_calc2(
            torr, Phase.M, tcurr, self.integrated2_mat, 1
        )
        self.assertAlmostEqual(torr, 0.083850562945195328, 10)

        pass

    def test_de_integrator(self):
        """
        This unit test is tests de_integrator which is used by vol_phantom_frac2(). The method uses
        3 different methods to calculate the Double Exponential Transformation.
        Method 1 is used for Li's algorithm
        Method 2 is used for Kirk83 algorithm
        Method 3 is used for Kirk83 algorithm for the Bianite curves
        """
        err = None
        nn = None
        # ===== Test for method 1 ===== #
        xf = self.sim_inst.nuc_start * self.sim_inst.xfe
        sig_int_ferrite = None
        sig_int_ferrite = self.simulation.test_de_integrator(
            sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, method=1
        )
        self.assertAlmostEqual(sig_int_ferrite, 0.10097017653666272, 10)

        # ===== Test for method 2 ===== #
        xf = self.sim_inst.nuc_start / self.sim_inst.xfe
        sig_int_ferrite = None
        sig_int_ferrite = self.simulation.test_de_integrator(
            sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2
        )
        self.assertAlmostEqual(sig_int_ferrite, 0.65227162834046781, 10)
        # ===== Test for method 3 ===== #
        xb = self.sim_inst.nuc_start
        sig_int_bainite = None
        sig_int_bainite = self.simulation.test_de_integrator(
            sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3
        )
        self.assertAlmostEqual(sig_int_bainite, 0.64064546121071431, 10)

    def test_sigmoid2(self):
        self.assertAlmostEqual(
            self.simulation.test_sigmoid2(0.49950000000000006),
            1.3195087024781862, 10
        )

    def test_imoid(self):
        self.assertAlmostEqual(
            self.simulation.test_imoid(0.49950000000000006),
            1.5874026393706624, 10
        )

    def test_imoid_prime2(self):
        self.assertAlmostEqual(
            self.simulation.test_imoid_prime2(0.49950000000000006),
            3.2311093572469849, 10
        )


class TestCoolingCurveTemperature(BaseConfigurationTest):
    def setUp(self) -> None:
        sim_inst = SimConfiguration(debug=True)
        self.simulation = PhaseSimulation(sim_inst, debug=True)
        # Init some common variables
        self.sorted_ccr = None

    def test_ccr(self):
        integrated2_mat = np.zeros((4, 11), dtype=np.float64)
        self.simulation.test_vol_phantom_frac2(integrated2_mat)
        ccr_mat = np.zeros((3, 2), dtype=np.float64)

        self.simulation.test_critical_cooling_rate(
            ccr_mat, self.simulation.ms, self.simulation.bs,
            self.simulation.ae1, self.simulation.ae3, integrated2_mat
        )
        # logger.pprint(ccr_mat)
        # Ferrite CCR
        self.assertAlmostEqual(ccr_mat[0, 0], 158.9194157771073, 10)
        self.assertAlmostEqual(ccr_mat[0, 1], 158.9194157771073, 10)
        # Pearlite CCR
        self.assertAlmostEqual(ccr_mat[1, 0], 0.21889237213174512, 10)
        self.assertAlmostEqual(ccr_mat[1, 1], 0.21889237213174512, 10)
        # Bainite CCR
        self.assertAlmostEqual(ccr_mat[2, 0], 799.11526317494611, 10)
        self.assertAlmostEqual(ccr_mat[2, 1], 41.167590371658619, 10)

        self.sorted_ccr = sort_ccr(ccr_mat=ccr_mat)

    def test_cct(self):
        res = self.simulation.cct()

        logger.info(res['ferrite_nucleation'][0:9, :])
        logger.info(res['martensite'][0:9, :])


if __name__ == '__main__':
    unittest.main()
