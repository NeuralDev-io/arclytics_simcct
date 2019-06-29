# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# simulations.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Arvy Salazar <@Xaraox>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.29'

"""simulations.py: 

{Description}
"""

# Built-in/Generic Imports
import os
import math
# Libs
# Own modules


class Simulation(object):
    # ======= TEMPORARY VARIABLES ======= #

    # ======= TEMPORARY VARIABLES ======= #

    def __init__(self, sim_configurations, debug=False):
        if debug:
            self.sim_configurations = sim_configurations
            # TODO not sure how to get parent compositions from sim_configurations
        else:
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

            self.METHOD = "Kirk83" # Li98 and Kirk83
            self.START_PERCENT = 1 / 100
            self.FINISH_PERCENT = 99.9 / 100

            self.XFE = 0.946210268948655
            self.XBR = 1.0

            self.G = 8.0

            self.AE1 = 701
            self.AE3 = 845.8379611854

    def ttt(self):
        # FIXME I have removed X and Xpct are not used. Ask if it can be removed.
        w, h = 11, 4
        integrated2 = [[0 for x in range(w)] for y in range(h)]

        self.__vol_phantom_frac2(integrated2)

        torr = 0.0
        # ========= FERRITE PHASE ========= #
        phase = "F"
        w, h = 2, 10001
        fcs = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve start
        fcf = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve finish

        for I in range(1, 3):
            tcurr = self.BS - 50
            count_fn = 0
            while tcurr < (self.AE3 - 1):
                torr = self.__torr_calc2(torr, phase, tcurr, integrated2, I)

                if I is 1:
                    fcs[count_fn][0] = torr
                    fcs[count_fn][1] = tcurr
                else:
                    fcf[count_fn][0] = torr
                    fcf[count_fn][1] = tcurr

                count_fn = count_fn + 1
                tcurr = tcurr + 1

        # ========= PEARLITE PHASE ========= #
        phase = "P"
        w, h = 2, 10001
        pcs_vect = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve start
        pcf_vect = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve finish

        for I in range(1, 3):
            tcurr = self.BS - 50
            count_pn = 0
            while tcurr < (self.AE1 - 1):
                torr = self.__torr_calc2(torr, phase, tcurr, integrated2, I)
                if I is 1:
                    pcs_vect[count_pn][0] = torr
                    pcs_vect[count_pn][1] = tcurr
                else:
                    pcf_vect[count_pn][0] = torr
                    pcf_vect[count_pn][1] = tcurr

                count_pn = count_pn + 1
                tcurr = tcurr + 1

        # ========= BIANITE PHASE ========= #
        phase = "B"
        w, h = 2, 10001
        bcs_vect = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve start
        bcf_vect = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve finish

        for I in range(1, 3):
            count_bn = 0
            tcurr = self.MS

            while tcurr < (self.BS - 1):
                torr = self.__torr_calc2(torr, phase, tcurr, integrated2, I)

                if I is 1:
                    bcs_vect[count_bn][0] = torr
                    bcs_vect[count_bn][1] = tcurr
                else:
                    bcf_vect[count_bn][0] = torr
                    bcf_vect[count_bn][1] = tcurr
                count_bn = count_bn + 1
                tcurr = tcurr + 1

        # ========= MANTENSITE ========= #
        w, h = 2, 3  # CHANGE Used to be (2,100001) now has (2,3)
        msf_vect = [[0 for x in range(w)] for y in range(h)]  # Ferrite curve start
        tcurr = self.MS
        torr = self.__torr_calc2(torr, phase, tcurr, integrated2, I)
        # Uses Bianite cutoff time. So uses the Bianite phase as the argument

        msf_vect[1][0] = 0.001
        msf_vect[1][1] = self.MS
        msf_vect[2][0] = torr
        msf_vect[2][1] = self.MS


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


    def __de_integrator(self, i, a, b, eps, err, nn, method):
        # FIXME Check if err and nn are needed to be returned somewhere in the code as they are passed by reference.
        n = 0
        # Adjustable parameters
        mmax = 256
        efs = 0.1
        hoff = 8.5
        ##################################
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
            ir = self.sigmoid2((a + b) * 0.5) * (ba * 0.25)
        elif method is 2:
            ir = self.imoid2((a + b) * 0.5) * (ba * 0.25)
        elif method is 3:
            ir = self.imoid_prime2((a + b) * 0.5) * (ba * 0.25)
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
                        fa = self.sigmoid2(a + xa) * wg
                        fb = self.sigmoid2(b - xa) * wg
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


    def __vol_phantom_frac2(self, integrated_vect):
        err = None
        nn = None
        if self.METHOD == "Li98":

            # Ferrite Start
            xf = self.self.START_PERCENT * self.self.XFE

            integrated_vect[2][5] = xf

            sig_int_ferrite = 0
            sig_int_ferrite = self.__self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 1)
            integrated_vect[2][0] = sig_int_ferrite

            # Pearlite Start
            xpe = 1.0 - self.self.XFE
            # CheckPhantomTestP.Checked is always false because it is by default false and invisible
            xp = self.self.START_PERCENT / (1 - self.self.XFE)
            integrated_vect[2][6] = xp

            sig_int_pearlite, sig_int_pearlite_t = None, None
            # FIXME sig_int_pearlite_t is not used. Ask if it can be removed
            sig_int_pearlite = self.__self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 1)
            integrated_vect[2][1] = sig_int_pearlite

            xb = self.self.START_PERCENT

            integrated_vect[2][7] = xb

            sig_int_bainite = 0
            sig_int_bainite = self.__self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 1)
            integrated_vect[2][2] = sig_int_bainite

            ##########################################################

            # Ferrite Finish

            xf = self.FINISH_PERCENT * self.XFE
            if xf > 1.0:
                xf = 0.9999999

            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 1)
            integrated_vect[3][0] = sig_int_ferrite

            # Pearlite Finish

            xp = self.FINISH_PERCENT / (1 - self.XFE)
            if xp >= 1.0:
                xp = 0.9999999

            # this might not be needed it is calculated but not used anywhere else in the code.
            # FIXME sig_int_pearlite_t not used. Ask if it can be removed.
            sig_int_pearlite_t = self.__get_sx_integral(sig_int_pearlite_t, xp)
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 1)
            integrated_vect[3][1] = sig_int_pearlite

            # Bainite

            xb = self.FINISH_PERCENT
            if xb >= 1.0:
                xb = 0.9999999

            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 1)
            integrated_vect[3][2] = sig_int_bainite
        elif self.METHOD == "Kirk83":
            # FERRITE START
            xf = self.START_PERCENT / self.XFE
            sig_int_ferrite = 0
            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2)
            integrated_vect[0][0] = sig_int_ferrite

            # PEARLITE START
            xp = self.START_PERCENT / (1 - self.XFE)
            sig_int_pearlite = 0
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 2)
            integrated_vect[0][1] = sig_int_pearlite

            # BIANITE START
            xb = self.START_PERCENT
            sig_int_bainite = 0
            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3)
            integrated_vect[0][2] = sig_int_bainite

            # FERRITE FINISH
            xf = self.FINISH_PERCENT * self.XFE
            sig_int_ferrite = 0
            sig_int_ferrite = self.__de_integrator(sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2)
            integrated_vect[1][0] = sig_int_ferrite

            # PEARLITE FINISH
            xp = self.FINISH_PERCENT * (1 - self.XFE)
            if xp >= 1.0:
                xp = 0.9999999
            sig_int_pearlite = 0
            sig_int_pearlite = self.__de_integrator(sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 2)
            integrated_vect[1][1] = sig_int_pearlite

            # BIANITE FINISH
            xb = self.FINISH_PERCENT
            if xb >= 1.0:
                xb = 0.9999999
            sig_int_bainite = 0
            sig_int_bainite = self.__de_integrator(sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3)
            integrated_vect[1][2] = sig_int_bainite

    def __torr_calc2(self, torr, phase, tcurr, integral2_vect, I):

        R_GAS = 1.985

        if self.METHOD == "Li98":

            sint_f = integral2_vect[I + 1][0]
            sint_p = integral2_vect[I + 1][1]
            sint_b = integral2_vect[I + 1][2]

            if phase == "F":
                fc = math.exp(1.0 + 6.31 * self.p_comp['C'] + 1.78 * self.p_comp['Mn'] + 0.31 * self.p_comp['Si'] +
                              1.12 * self.p_comp['Ni'] + 2.7 * self.p_comp['Cr'] + 4.06 * self.p_comp['Mo'])
                return fc / (2 ** (0.41 * self.G) * ((self.AE3 - tcurr) ** 3) *
                             math.exp(-27500 /(R_GAS * (tcurr + 273)))) * sint_f
            elif phase == "P":
                pc = math.exp(-4.25 + 4.12 * self.p_comp['C'] + 4.36 * self.p_comp['Mn'] + 0.44 * self.p_comp['Si'] +
                              1.71 * self.p_comp['Ni'] + 3.33 * self.p_comp['Cr'] + 5.19 * math.sqrt(self.p_comp['Mo']))
                return pc / (2 ** (0.32 * self.G) * ((self.AE1 - tcurr) ** 3) * math.exp(
                    -27500 / (R_GAS * (tcurr + 273)))) * sint_p
            elif phase == "B":
                bc = math.exp(-10.23 + 10.18 * self.p_comp['C'] + 0.85 * self.p_comp['Mn'] + 0.55 * self.p_comp['Ni'] +
                              0.9 * self.p_comp['Cr'] + 0.36 * self.p_comp['Mo'])
                return bc / (
                            2 ** (0.29 * self.G) * ((self.BS - tcurr) ** 2) * math.exp(-27500 / (R_GAS * (tcurr + 273)))) * sint_b
        elif self.METHOD == "Kirk83":
            iint_f = integral2_vect[I - 1][0]
            iint_p = integral2_vect[I - 1][1]
            iint_b = integral2_vect[I - 1][2]

            if phase == "F":
                fc = (59.6 * self.p_comp['Mn'] + 1.45 * self.p_comp['Ni'] + 67.7 * self.p_comp['Cr'] + 244 * self.p_comp['Mo'])
                return fc / (2 ** ((self.G - 1) / 2) * ((self.AE3 - tcurr) ** 3) * math.exp(-23500 /
                                                                                  (R_GAS * (tcurr + 273)))) * iint_f
            elif phase == "P":
                pc = 1.79 + 5.42 * (self.p_comp['Cr'] + self.p_comp['Mo'] + 4 * self.p_comp['Mo'] * self.p_comp['Ni'])
                dinv = (1 / math.exp(-27500 / (R_GAS * (tcurr + 273)))) + \
                       ((0.01 * self.p_comp['Cr'] + 0.52 * self.p_comp['Mo']) /math.exp(-37500 / (R_GAS * (tcurr + 273))))
                return pc / ((2 ** ((self.G - 1) / 2) * ((self.AE1 - tcurr) ** 3) * (1 / dinv)) * iint_p)
            elif phase == "B":
                bc = (2.34 + 10.1 * self.p_comp['C'] + 3.8 * self.p_comp['Cr'] + 19.0 * self.p_comp['Mo']) * 10 ** -4
                return bc / (2 ** ((self.G - 1) / 2) * ((self.BS - tcurr) ** 2) * math.exp(-27500 /
                                                                                 (R_GAS * (tcurr + 273)))) * iint_b