# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# simulations.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Arvy Salazar <@Xaraox>', 'Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.29'

"""simulations.py: 

{Description}
"""

import math
import enum

import numpy as np

from logger.arc_logger import AppLogger
from simulation.utilities import Method, Alloy
from simulation.simconfiguration import SimConfiguration

logger = AppLogger(__name__)


class Phase(enum.Enum):
    F = 1
    P = 2
    B = 3
    M = 4


class Simulation(object):
    XBR = 1.0

    def __init__(self, sim_configs: SimConfiguration = None, debug=False):
        if debug:
            self.sim_configs = sim_configs
            self.start_percent = self.sim_configs.nuc_start
            self.finish_percent = self.sim_configs.nuc_finish
            # TODO not sure how to get parent compositions from sim_configurations

        if sim_configs is None:
            self.p_comp = {
                'C': 0.044,
                'P': 0.0,
                'Mn': 1.730,
                'Si': 0.220,
                'Ni': 0.000,
                'Cr': 0.000,
                'Mo': 0.260,
                'Al': 0.0,
                'Cu': 0.0,
                'As': 0.0,
                'Ti': 0.0,
                'Co': 0.000,
                'V': 0.0,
                'W': 0.0,
                'S': 0.0,
                'N': 0.0,
                'Nb': 0.0,
                'B': 0.0,
                'Fe': 0.0
            }

            self.MS = 464
            self.BS = 563

            self.METHOD = "Kirk83"  # Li98 and Kirk83
            self.START_PERCENT = 1 / 100
            self.FINISH_PERCENT = 99.9 / 100

            self.XFE = 0.946210268948655
            self.XBR = 1.0

            self.G = 8.0

            self.AE1 = 701
            self.AE3 = 845.8379611854

        self.debug = debug

    def ttt(self):
        # FIXME I have removed X and Xpct are not used. Ask if it can be removed.

        if self.debug:
            ms = round(self.sim_configs.ms_temp)
            bs = round(self.sim_configs.bs_temp)

        integrated2_mat = np.zeros((4, 11), dtype=np.float64)

        self.__vol_phantom_frac2(integrated2_mat)

        torr = 0.0
        # ========= FERRITE PHASE ========= #
        phase = Phase.F

        fcs_mat = np.zeros((10001, 2), dtype=np.float64)  # Ferrite Curve Start
        fcf_mat = np.zeros((10001, 2), dtype=np.float64)  # Ferrite Curve Finish

        for i in range(1, 3):
            tcurr = bs - 50
            count_fn = 0
            while tcurr < (self.AE3 - 1):
                torr = self.__torr_calc2(torr, phase, tcurr, integrated2_mat, i)

                if i is 1:
                    fcs_mat[count_fn, 0] = torr
                    fcs_mat[count_fn, 1] = tcurr
                else:
                    fcf_mat[count_fn, 0] = torr
                    fcf_mat[count_fn, 1] = tcurr

                count_fn = count_fn + 1
                tcurr = tcurr + 1

        # ========= PEARLITE PHASE ========= #
        phase = Phase.P
        pcs_mat =  np.zeros((10001, 2), dtype=np.float64) # Ferrite curve start
        pcf_mat = np.zeros((10001, 2), dtype=np.float64)  # Ferrite curve finish

        for i in range(1, 3):
            tcurr = bs - 50
            count_pn = 0

            while tcurr < (round(self.sim_configs.ae1) - 1):
                torr = self.__torr_calc2(torr, phase, tcurr, integrated2_mat, i)
                if i is 1:
                    pcs_mat[count_pn, 0] = torr
                    pcs_mat[count_pn, 1] = tcurr
                else:
                    pcf_mat[count_pn, 0] = torr
                    pcf_mat[count_pn, 1] = tcurr

                count_pn = count_pn + 1
                tcurr = tcurr + 1

        # ========= BAINITE PHASE ========= #
        phase = Phase.B
        bcs_mat = np.zeros((10001, 2), dtype=np.float64)  # Ferrite curve start
        bcf_mata = np.zeros((10001, 2), dtype=np.float64) # Ferrite curve finish

        for i in range(1, 3):
            count_bn = 0
            tcurr = ms

            while tcurr < (bs - 1):
                torr = self.__torr_calc2(torr, phase, tcurr, integrated2_mat, i)

                if i is 1:
                    bcs_mat[count_bn, 0] = torr
                    bcs_mat[count_bn, 1] = tcurr
                else:
                    bcf_mata[count_bn, 0] = torr
                    bcf_mata[count_bn, 1] = tcurr
                count_bn = count_bn + 1
                tcurr = tcurr + 1

        # ========= MARTENSITE ========= #
        msf_vect = np.zeros((3, 2), dtype=np.float64) # Ferrite curve start
        tcurr = ms
        torr = self.__torr_calc2(torr, phase, tcurr, integrated2_mat, i)
        # Uses Bainite cutoff time. So uses the Bainite phase as the argument

        msf_vect[1, 0] = 0.001
        msf_vect[1, 1] = ms
        msf_vect[2, 0] = torr
        msf_vect[2, 1] = ms

    def cct(self):
        # Can be used for any cooling path new routine to simplify iterative routines using any of the methods
        # coded in. Should be much simpler to code and follow and only needs to be done once not repeated for each
        # method as before

        # The equilibrium phase fraction of ferrite at the eutectic temperature
        # (consistent with Kirkaldy implementation and explained by Watt et. al. 88)
        if self.sim_configs.xfe >= 1.0:
            logger.error('XFE has to be below 1.0')
        else:
            xfe = self.sim_configs.xfe

        x_pct_vect = np.array([self.finish_percent, self.start_percent])
        pwd = self.sim_configs.alloy.value

        # Volume fraction remaining for potential Bainite precipitation. Starts at 1.0 but may reduce if in CCT mode
        # if Ferrite/Pearlite already formed
        x_br = np.float64(1.0)

        # Transformation time Ferrite, Pearlite, Bainite respectively
        torr_f, torr_p, torr_b = None, None, None
        torr_f_end, torr_p_end, torr_b_end = None, None, None

        # Set fraction of nucleation
        nuc_frac_austenite = np.float64(1.0)
        nuc_frac_ferrite = np.float64(0)
        nuc_frac_pearlite = np.float64(0)
        nuc_frac_bainite = np.float64(0)
        nuc_frac_martensite = np.float64(0)
        # Set fraction of completion
        nuc_frac_austenite_end = np.float64(1.0)
        nuc_frac_ferrite_end = np.float64(0)
        nuc_frac_pearlite_end = np.float64(0)
        nuc_frac_bainite_end = np.float64(0)
        nuc_frac_martensite_end = np.float64(0)

        # Set initial grain size
        g_curr = self.sim_configs.grain_size

        # Kirkaldy:
        # [0,0], [0,1], [0,2] spots for starting precipitation
        # [1,0], [1,1], [1,2] spots for finishing precipitation
        # Li98:
        # [2,0], [2,1], [2,2] spots for starting precipitation
        # [3,0], [3,1], [3,2] spots for finishing precipitation
        integrated2_mat = np.zeros((4, 11), dtype=np.float64)

        # Get integrals for relevant % transformed  at nucleation (start) and finish
        self.__vol_phantom_frac2(integrated2_mat)

        temp_start = self.sim_configs.temp_peak

        # Trigger after Ferrite nucleation point has been found to stop the routine  recording for the
        # current cooling rate
        stop_f = None
        stop_p = None  # Pearlite trigger
        stop_b = None  # Bainite trigger
        # Trigger after Ferrite nucleation point has been found to stop the routine
        stop_f_end = None
        stop_p_end = None  # Pearlite trigger
        stop_b_end = None  # Bainite trigger

        # ========== # TIME LOOP # ========== #
        # The time increments can be either constant cooling rate or follow a defined curve. Figure this out first and
        # populate an array containing discreet increments of time for the FOR loop to follow. The increment size does
        # not have to be constant as some segments can be run through quickly i.e. the cooling from initial temperature
        # to Ae3 only involves potential grain growth

        # Can hold 100000 time/temperature points for Ferrite nucleation temperature
        cct_record_f_mat = np.zeros((10000, 3), dtype=np.float64)  # Ferrite
        cct_record_p_mat = np.zeros((10000, 3), dtype=np.float64)  # Pearlite
        cct_record_b_mat = np.zeros((10000, 3), dtype=np.float64)  # Bainite
        cct_record_m_mat = np.zeros((10000, 3), dtype=np.float64)  # Martensite
        # Can hold 100000 time/temperature points for Ferrite finish temperature
        cct_record_f_end_mat = np.zeros((10000, 3), dtype=np.float64)  # Ferrite
        cct_record_p_end_mat = np.zeros((10000, 3), dtype=np.float64)  # Pearlite
        cct_record_b_end_mat = np.zeros((10000, 3), dtype=np.float64)  # Bainite

        # Counters
        ii_f, ii_p, ii_b, ii_m = 0, 0, 0, 0
        ii_f_end, ii_p_end, ii_b_end, ii_m_end = 0, 0, 0, 0

        # Find the critical cooling rates for each phase
        # Storage for critical cooling rates
        ccr = np.zeros((3, 2), dtype=np.float64)
        # CCR[0,0] - ferrite-init, CCR[0,1] - ferrite-finish
        # CCR(1,0] - pearlite-init, CCR[1,1] - pearlite-finish
        # CCR[2,0] - bainite-init, CCR[2,1] - bainite-finish
        # UPDATE CCR[] to CALL CriticalCR(CCR[], Method, G, MS, BS, Ae1, Ae3, Comp, Integral2, Alloy)
        self.__critical_cooling_rate(ccr, self.sim_configs.grain_size, self.sim_configs.ms_temp,
                                     self.sim_configs.bs_temp, self.sim_configs.ae1, self.sim_configs.ae3,
                                     self.sim_configs.comp_parent.copy(), integrated2_mat, pwd)

    def __sigmoid2(self, x):
        return 1 / ((x ** (0.4 * (1 - x))) * ((1 - x) ** (0.4 * x)))

    def __imoid(self, x):
        return 1 / ((x ** (2.0 * (1 - x) / 3)) * ((1 - x) ** (2.0 * x / 3)))

    def __imoid_prime2(self, x):
        numerator = math.exp(x ** 2.0 * (1.9 * self.p_comp['C'] + 2.5 * self.p_comp['Mn'] + 0.9 * self.p_comp['Ni'] +
                                         1.7 * self.p_comp['Cr'] + 4.0 * self.p_comp['Mo'] - 2.6))
        b = (1.9 * self.p_comp['C'] + 2.5 * self.p_comp['Mn'] + 0.9 * self.p_comp['Ni'] + 1.7 * self.p_comp['Cr'] + 4.0
             * self.p_comp['Mo'] - 2.6)
        if b < 0:
            return 1 / ((x ** (2.0 * (1 - x) / 3.0)) * ((1 - x) ** (2.0 * x / 3.0)))
        else:
            return numerator / ((x ** (2.0 * (1 - x) / 3.0)) * ((1 - x) ** (2.0 * x / 3.0)))

    def __get_sx_integral(self, x):
        if (x >= 0.00) and (x < 0.01):
            return 1.7635 * x ** 0.6118
        if (x >= 0.01) and (x < 0.5):
            return 1.5401 * x ** 0.5846
        if (x >= 0.5) and (x < 0.95):
            return 1.4 * x ** 2 - 0.45 * x + 0.936
        if (x >= 0.95) and (x <= 1.0):
            return 2383.21 * x ** 3 - 6891.57 * x ** 2 + 6646 * x - 2135.57

    def __de_integrator(self, i, a, b, eps, err, nn, method):
        # FIXME Check if err and nn are needed to be returned somewhere in the code as they are passed by reference.
        n = 0
        # Adjustable parameters
        mmax = 256
        efs = 0.1
        hoff = 8.5
        # ======================================== #
        pi2 = 2 * math.atan(1.0)
        epsln = 1 - math.log(efs * eps)
        epsh = math.sqrt(efs * eps)
        h0 = hoff / epsln
        ehp = math.exp(h0)
        ehm = 1 / ehp
        epst = math.exp(-ehm * epsln)
        ba = b - a
        ir = 0.0
        fa = 0.0
        fb = 0.0

        if method is 1:
            ir = self.__sigmoid2((a + b) * 0.5) * (ba * 0.25)
        elif method is 2:
            ir = self.__imoid((a + b) * 0.5) * (ba * 0.25)
        elif method is 3:
            ir = self.__imoid_prime2((a + b) * 0.5) * (ba * 0.25)
        n = n + 1

        i = ir * (2 * pi2)
        err = abs(i) * epst
        h = 2 * h0
        m = 1

        while True:
            iback = i
            irback = ir
            t = h * 0.5
            while True:
                em = math.exp(t)
                ep = pi2 * em
                em = pi2 / em
                while True:
                    xw = 1 / (1 + math.exp(ep - em))
                    xa = ba * xw
                    wg = xa * (1 - xw)

                    if method is 1:
                        fa = self.__sigmoid2(a + xa) * wg
                        fb = self.__sigmoid2(b - xa) * wg
                    elif method is 2:
                        fa = self.imoid2(a + xa) * wg
                        fb = self.imoid2(b - xa) * wg
                    elif method is 3:
                        fa = self.imoid_prime2(a + xa) * wg
                        fb = self.imoid_prime2(b - xa) * wg
                    n = n + 2
                    ir = ir + (fa + fb)
                    i = i + (fa + fb) * (ep + em)
                    errt = (abs(fa) + abs(fb)) * (ep + em)
                    if m is 1:
                        err = err + errt * epst
                    ep = ep * ehp
                    em = em * ehm
                    if (errt <= err) and (xw <= epsh):
                        break
                t = t + h
                if t >= h0:
                    break
            if m is 1:
                errh = (err / epst) * epsh * h0
                errd = 1 + 2 * errh
            else:
                errd = h * (abs(i - 2 * iback) + 4 * abs(ir - 2 * irback))
            h = h * 0.5
            m = m * 2
            if (errd <= errh) or (m >= mmax):
                break

        i = i * h
        if errd > errh:
            err = -errd * m
        else:
            err = errh * epsh * m / (2 * efs)

        nn = n
        return i

    def __vol_phantom_frac2(self, integrated_mat) -> None:
        """This routine will return the expected volume or phantom fraction for the specific methodology being
        requested by the USER defined precipitation points for starting and finishing.

        xfe: equilibrium phase fraction of ferrite.
        xbr: remaining volume available for transformation to Bainite. Will be = 1.0 for TTT but may be lower in CCT if
             Ferrite and Pearlite have already formed.

        nuc_start: the requested start %. usually 1.0% or 0.1% (converted to a fraction i.e. 0.01 or 0.001 respectively).
        nuc_finish: the requested end %. usually 99.9% (converted to a fraction. i.e. 0.999)

        Definitions of "integrated_mat[,]"
        Kirkaldy:
        [0,0], [0,1], [0,2]: spots for starting precipitation of F, P, and B respectively.
        [1,0], [1,1], [1,2]: spots for finishing precipitation of F, P, and B respectively.

        Li98:
        [2,0], [2,1], [2,2]: spots for starting precipitation of F, P, and B respectively
        [3,0], [3,1], [3,2]: spots for finishing precipitation of F, P, and B respectively

        Args:
            integrated_mat: definition above.

        Returns:
            None
        """
        err = None
        nn = None

        if self.sim_configs.method == Method.Li98:

            # Ferrite Start
            xf = self.start_percent * self.sim_configs.xfe

            integrated_mat[2, 5] = xf

            sig_int_ferrite = 0
            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 1)
            integrated_mat[2, 0] = sig_int_ferrite

            # Pearlite Start
            xpe = 1.0 - self.sim_configs.xfe
            # CheckPhantomTestP.Checked is always false because it is by default false and invisible
            xp = self.start_percent / (1 - self.sim_configs.xfe)
            integrated_mat[2, 6] = xp

            sig_int_pearlite, sig_int_pearlite_t = None, None
            # FIXME sig_int_pearlite_t is not used. Ask if it can be removed
            sig_int_pearlite_t = self.__get_sx_integral(xp)
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 1)
            integrated_mat[2, 1] = sig_int_pearlite

            xb = self.start_percent

            integrated_mat[2, 7] = xb

            sig_int_bainite = 0
            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 1)
            integrated_mat[2, 2] = sig_int_bainite

            # ======================================================================================================= #

            # Ferrite Finish

            xf = self.finish_percent * self.sim_configs.xfe
            if xf > 1.0:
                xf = 0.9999999

            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 1)
            integrated_mat[3, 0] = sig_int_ferrite

            # Pearlite Finish
            xp = self.finish_percent / (1 - self.sim_configs.xfe)
            if xp >= 1.0:
                xp = 0.9999999

            # FIXME sig_int_pearlite_t not used. Ask if it can be removed.
            sig_int_pearlite_t = self.__get_xs_integral(xp)
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 1)
            integrated_mat[3, 1] = sig_int_pearlite

            # Bainite

            xb = self.finish_percent
            if xb >= 1.0:
                xb = 0.9999999

            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 1)
            integrated_mat[3, 2] = sig_int_bainite

        elif self.sim_configs.method == Method.Kirkaldy83:
            # FERRITE START
            xf = self.start_percent / self.sim_configs.xfe
            sig_int_ferrite = 0
            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2)
            integrated_mat[0, 0] = sig_int_ferrite

            # PEARLITE START
            xp = self.start_percent / (1 - self.sim_configs.xfe)
            sig_int_pearlite = 0
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 2)
            integrated_mat[0, 1] = sig_int_pearlite

            # BAINITE START
            xb = self.start_percent
            sig_int_bainite = 0
            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3)
            integrated_mat[0, 2] = sig_int_bainite

            # FERRITE FINISH
            xf = self.finish_percent * self.sim_configs.xfe
            sig_int_ferrite = 0
            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2)
            integrated_mat[1, 0] = sig_int_ferrite

            # PEARLITE FINISH
            xp = self.finish_percent * (1 - self.sim_configs.xfe)
            if xp >= 1.0:
                xp = 0.9999999
            sig_int_pearlite = 0
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 2)
            integrated_mat[1, 1] = sig_int_pearlite

            # BAINITE FINISH
            xb = self.finish_percent
            if xb >= 1.0:
                xb = 0.9999999
            sig_int_bainite = 0
            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3)
            integrated_mat[1, 2] = sig_int_bainite

    def __torr_calc2(self, torr: float, phase: Phase, tcurr: float, integral2_mat: np.ndarray, i: int) -> float:
        R_GAS = 1.985

        wt = self.sim_configs.comp_parent
        c = wt['weight'][wt['name'] == 'carbon'][0]
        mn = wt['weight'][wt['name'] == 'manganese'][0]
        si = wt['weight'][wt['name'] == 'silicon'][0]
        mo = wt['weight'][wt['name'] == 'molybdenum'][0]
        ni = wt['weight'][wt['name'] == 'nickel'][0]
        cr = wt['weight'][wt['name'] == 'chromium'][0]
        g = self.sim_configs.grain_size
        ae1 = self.sim_configs.ae1
        ae3 = self.sim_configs.ae3
        bs = self.sim_configs.bs_temp

        if self.debug:
            bs = round(self.sim_configs.bs_temp)
            ae1 = round(self.sim_confis.ae1)

        if self.sim_configs.method == Method.Li98:

            sint_f = integral2_mat[i + 1, 0]
            sint_p = integral2_mat[i + 1, 1]
            sint_b = integral2_mat[i + 1, 2]

            if phase == Phase.F:
                fc = np.float64(
                    math.exp(1.0 + (6.31 * c) + (1.78 * mn) + (0.31 * si) + (1.12 * ni) + (2.7 * cr) + (4.06 * mo))
                )

                return np.float64(
                    fc /
                    (math.pow(2, (0.41*g)) * math.pow((ae3 - tcurr), 3) * math.exp(-27500 / (R_GAS * (tcurr + 273)))) *
                    sint_f
                )

            elif phase == Phase.P:
                pc = np.float64(
                    math.exp(-4.25 + (4.12 * c) + (4.36 * mn) + (0.44 * si) + (1.71 * ni) + (3.33 * cr) +
                             (5.19 * math.sqrt(mo)))
                )

                return np.float64(
                    pc /
                    (math.pow(2, (0.32*g)) * math.pow((round(ae1) - tcurr), 3) * math.exp(-27500 /
                                                                                          (R_GAS * (tcurr + 273)))) *
                    sint_p
                )

            elif phase == Phase.B:
                bc = np.float64(math.exp(-10.23 + (10.18 * c) + (0.85 * mn) + (0.55 * ni) + (0.9 * cr) + (0.36 * mo)))

                return np.float64(
                    bc /
                    (math.pow(2, (0.29 * g)) * math.pow((bs - tcurr), 2) * math.exp(-27500 / (R_GAS * (tcurr + 273)))) *
                    sint_b
                )

        elif self.sim_configs.method == Method.Kirkaldy83:
            iint_f = integral2_mat[i - 1, 0]
            iint_p = integral2_mat[i - 1, 1]
            iint_b = integral2_mat[i - 1, 2]

            if phase == Phase.F:
                fc = np.float64(((59.6 * mn) + (1.45 * ni) + (67.7 * cr) + (244 * mo)))

                return fc / (2 ** ((g - 1) / 2) * ((ae3 - tcurr) ** 3) *
                             math.exp(-23500 / (R_GAS * (tcurr + 273)))) * iint_f

            elif phase == Phase.P:
                pc = np.float64(1.79 + 5.42 * (cr + mo + 4 * mo * ni))
                dinv = (1 / math.exp(-27500 / (R_GAS * (tcurr + 273)))) + \
                       ((0.01 * cr + 0.52 * mo) / math.exp(-37500 / (R_GAS * (tcurr + 273))))

                return pc / ((2 ** ((g - 1) / 2) *
                              ((self.sim_configs.ae1 - tcurr) ** 3) * (1 / dinv)) * iint_p)

            elif phase == Phase.B:
                bc = np.float64((2.34 + (10.1 * c) + (3.8 * cr) + (19.0 * mo)) * math.pow(10, -4))

                return bc / (2 ** ((g - 1) / 2) * ((bs - tcurr) ** 2) *
                             math.exp(-27500 / (R_GAS * (tcurr + 273)))) * iint_b

        return -1

    def __critical_cooling_rate(
            self, ccr: np.ndarray, g: float, ms: float, bs: float, ae1: float, ae3: float,
            comp: np.ndarray, integrated2: np.ndarray, pwd: int):
        """

        Args:
            ccr:
            g:
            ms:
            bs:
            ae1:
            ae3:
            comp:
            integrated2:
            phase:
            pwd:

        Returns:

        """

        # Current temperature
        temp_curr = np.float(0)

        # ========== # BAINITE CCR # ========== #
        phase = Phase.B
        torr_b, ccr_bcs = np.float64(0), np.float64(0)
        time_accumulate = 0
        # initialise the time interval for this loop
        time_interval = 1.0

        # Start at Martensite temperature and work up to Bainite limit
        temp_curr = self.sim_configs.ms_temp

        while temp_curr < self.sim_configs.bs_temp:
            # Get isothermal nucleation time at current temperature
            torr_b = self.__torr_calc2(torr_b, phase=phase, tcurr=temp_curr, integral2_mat=integrated2, i=1)

            # Bainite start. Accumulation ratio
            ccr_bcs = ccr_bcs + (time_interval / torr_b)
            temp_curr = temp_curr + 1
            time_accumulate = time_accumulate + time_interval

        ccr[2, 0] = ccr_bcs / ((self.sim_configs.bs_temp - self.sim_configs.ms_temp) /
                               (time_accumulate - time_interval))
