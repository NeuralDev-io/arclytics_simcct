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
# Libs
# Own modules

class Simulations(object):
    # ======= TEMPORARY VARIABLES ======= #
    p_comp = {
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

    MS = 464
    BS = 563

    METHOD = "Kirk83"
    # Li98 and Kirk83
    START_PERCENT = 1 / 100
    FINISH_PERCENT = 99.9 / 100

    XFE = 0.946210268948655
    XBR = 1.0

    G = 8.0

    AE1 = 701
    AE3 = 845.8379611854
    # ======= TEMPORARY VARIABLES ======= #

    def __init__(self, sim_configurations):
        self.sim_configurations = sim_configurations

    def __vol_phantom_frac2(self, integrated2):
        #TODO implement this
        return

    def __de_integrator(self):
        # TODO implement this
        return

    def __torr_calc2(self, torr, phase, tcurr, integrated2, I):
        # TODO implement this
        return

    def ttt(self):
        # FIXME X and Xpct are not used. Ask if it can be removed
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
            tcurr = BS - 50
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
                torr = self__torr_calc2(torr, phase, tcurr, integrated2, I)

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
