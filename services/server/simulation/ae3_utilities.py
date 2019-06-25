# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# ae3_utilities.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.0.4'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.25'

"""ae3_utilities.py: 

This package combines in one file all the subroutines to calculate Ae3 and associated values required for Arclytics Sim.
Ae3 is calculated using ortho-equilibrium methods.
"""

import os
from typing import *
import numpy as np


def ae3_single_carbon(ae3: float, wt_comp: np.ndarray, wt_c: float) -> float:
    # Only passing in the original wt% alloys (note: C and Fe will be
    # overwritten below for each iteration of the main loop)
    t0 = 0.0
    # TODO: Not really sure why we need AI but whatever
    ai = np.zeros(20, dtype=np.float64)

    # Reset wt% carbon in array to zero (this will be updated below within the
    # main loop to match C)
    wt_comp['weight'][wt_comp['name'] == 'carbon'] = 0.0
    # Reset wt% Fe (Iron) in array to zero (this will be updated below within
    # the main loop)
    wt_comp['weight'][wt_comp['name'] == 'iron'] = 0.0

    return ae3_set_carbon(t0, ai, wt_comp, wt_c)


def ae3_set_carbon(t0: float, ai: np.array, wt: np.ndarray, c: float) -> float:
    """
    Calculate Ae3 for fixed value of carbon (C).
    Args:
        t0:
        ai:
        wt:
        c:

    Returns:

    """
    _R = np.float64(1.9858)
    _g = _gc = _t = _h = _cf = np.float64(0.0)
    _sum = _delta_t =  np.float64(0.0)

    _tt = np.float64(0.0)
    _z = np.float64(0.0)

    # add the wt%s to find the total (without C and Fe which update with
    # each increment in the loop)
    wt_pc = np.sum(wt['weight'])

    # add the current Carbon wt% to the total for this iteration
    wt_pc = wt_pc + c
    wt['weight'][wt['name'] == 'iron'] = 100 - wt_pc  # wt% Fe by difference
    wt['weight'][wt['name'] == 'carbon'] = c

    # Now convert to mole fraction for updated composition with this iteration
    _x = np.zeros(wt.shape[0], dtype=np.float64)  # mole fractions of all elements
    _yy = np.zeros(wt.shape[0], dtype=np.float64)  # mole fractions of Fe (not used)

    # TODO: Check that the _yy is redundant and not used
    wt, _x, _y = convert_wt_2_mol(wt, _x, _yy)

    _fe_af = _x[-1]  # moles Fe
    _c_af = _x[0]  # moles C

    # Add all the other element moles
    _add = np.sum(_x[1:-1])

    # Total of all moles added
    # _total_af = _fe_af + _c_af + _add
    _total_af = np.sum(_x)

    # Fraction of carbon moles to all moles (mole fraction C).
    _cf = _c_af / _total_af

    # Mole fraction of each element (excluding Carbon and Iron)
    _x = _x / _total_af

    t0 = tzero2(c)  # Using wt% C
    _t = t0  # starting point for evaluation

    _h1 = -15325.0
    _a = np.zeros(20, dtype=np.float64)

    _z = np.float64(1.0)  # Initialise before next while loop, just to get it going
    # Counter to determine and exit if non convergence occurs
    _counter = 0

    # while _z > 0.5:
    #     pass

    return _t


def convert_wt_2_mol(wt: np.ndarray, c: np.array, y: np.array) -> (np.ndarray, np.array, np.array):
    """
    Finds the mole fractions of each element
    Args:
        wt: weight % of each element in alloy composition
        c: mole fractions of each element with respect to the complete alloy composition (all elements).
        y: mole fraction of each element in relation to Fe only

    Returns:
    Tuple of each array updated.
    """

    b1 = 0
    _d = np.zeros(wt.shape[0])

    # Convert wt% to moles as if 100grams total

    # add all the wt% to find total wt% alloying elements
    # note: ensure last one with index -1 is Iron, Fe
    _d[-1] = np.sum(wt['weight'][wt['name'] != 'iron'])
    _d[-1] = 100.0 - _d[-1]  # find wt% Fe by difference
    _d[-1] = _d[-1] / 55.84  # Fe, calculate moles Fe if 100 g of alloy

    # TODO: What happens if we have more elements, how do we know what fractions?
    _d[0] = wt['weight'][wt['symbol'] == 'Cx'][0] / 12.0115      # Carbon
    _d[1] = wt['weight'][wt['symbol'] == 'Mn'][0] / 54.94        # Manganese
    _d[2] = wt['weight'][wt['symbol'] == 'Si'][0] / 28.09        # Silicon
    _d[3] = wt['weight'][wt['symbol'] == 'Ni'][0] / 58.71        # Nickel
    _d[4] = wt['weight'][wt['symbol'] == 'Cr'][0] / 52.0         # Chromium
    _d[5] = wt['weight'][wt['symbol'] == 'Mo'][0] / 95.94        # Molybdenum
    _d[6] = wt['weight'][wt['symbol'] == 'Co'][0] / 58.94        # Cobalt
    _d[7] = wt['weight'][wt['symbol'] == 'Al'][0] / 26.9815      # Aluminium
    _d[8] = wt['weight'][wt['symbol'] == 'Cu'][0] / 63.546       # Copper
    _d[9] = wt['weight'][wt['symbol'] == 'As'][0] / 74.9216      # Arsenic
    _d[10] = wt['weight'][wt['symbol'] == 'Ti'][0] / 47.867      # Titanium
    _d[11] = wt['weight'][wt['symbol'] == 'Vx'][0] / 50.9415     # Vanadium
    _d[12] = wt['weight'][wt['symbol'] == 'Wx'][0] / 183.85      # Tungsten
    _d[13] = wt['weight'][wt['symbol'] == 'Sx'][0] / 32.065      # Sulphur
    _d[14] = wt['weight'][wt['symbol'] == 'Nx'][0] / 14.0067     # Nitrogen
    _d[15] = wt['weight'][wt['symbol'] == 'Nb'][0] / 92.9064     # Niobium
    _d[16] = wt['weight'][wt['symbol'] == 'Bx'][0] / 10.811      # Boron
    _d[17] = wt['weight'][wt['symbol'] == 'Px'][0] / 30.9738     # Phosphorous

    b1 = np.sum(_d)

    # calculate mole fraction of each element with respect to the complete
    # alloy composition (all elements)
    c = _d / b1

    # calculate the mole fraction of each element in relation to Fe only
    y = c / c[-1]  # Fe is always the last element
    y[-1] = 0.0

    return wt, c, y


def tzero2(wt_c: float) -> float:
    """Returns pure iron t0 value with specified carbon wt %."""
    return 1115 - 154 * wt_c + 17.5 * np.power((1.2 - wt_c), 7.5)  # in C
