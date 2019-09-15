# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# ae3_utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.0.6'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.25'
__package__ = 'simulation'
"""ae3_utilities.py: 

This package combines in one file all the subroutines to calculate Ae3 and 
associated values required for Arclytics Sim. Ae3 is calculated using 
ortho-equilibrium methods.
"""

import math
import numpy as np

from .utilities import linear_fit
from .periodic import PeriodicTable as PT

# ========== # CONSTANTS # ========== #
R = np.float32(1.9858)


def ae3_single_carbon(wt_comp: np.ndarray, wt_c: float) -> float:
    # Only passing in the original wt% alloys (note: C and Fe will be
    # overwritten below for each iteration of
    # the main loop)
    ai_vect = np.zeros(20, dtype=np.float32)

    # Reset wt% carbon in array to zero (this will be updated below within
    # the main loop to match C)
    wt_comp['weight'][wt_comp['symbol'] == PT.C.name] = 0.0
    # Reset wt% Fe (Iron) in array to zero (this will be updated below within
    # the main loop)
    wt_comp['weight'][wt_comp['symbol'] == PT.Fe.name] = 0.0

    # This should actually update ai_vect and the return value to parent is ae3
    ae3, t0 = ae3_set_carbon(ai_vect, wt_comp, wt_c)
    return ae3


def ae3_set_carbon(
        ai_vect: np.array, wt_mat: np.ndarray, c: float
) -> (np.float, np.float):
    """
    Calculate Ae3 for fixed value of carbon (C).
    Args:
        t0:
        ai_vect:
        wt_mat:
        c:

    Returns:

    """

    # add the wt%s to find the total (without C and Fe which update with each
    # increment in the loop)
    # this is only for everything except carbon and iron but we already set
    # that to 0.0 previously
    wt_pc = np.sum(wt_mat['weight'])

    # add the current Carbon wt% to the total for this iteration
    wt_pc = wt_pc + c
    # wt% Fe by difference
    wt_mat['weight'][wt_mat['symbol'] == PT.Fe.name] = 100 - wt_pc
    wt_mat['weight'][wt_mat['symbol'] == PT.C.name] = c

    # Now convert to mole fraction for updated composition with this iteration
    # x_vect: mole fractions of all elements, with C as always index=0 and
    # Fe as always index=-1
    # y: # mole fractions of Fe (not used)
    x_vect, _ = convert_wt_2_mol(wt_mat)

    fe_af = x_vect[-1]  # moles Fe - NOTE: Iron is always the last element, -1
    c_af = x_vect[0]  # moles C

    # Add all the other element moles
    other_e_sum_af = np.sum(x_vect[1:-1], dtype=np.float32).astype(np.float32)

    # Total of all moles added
    total_af = fe_af + c_af + other_e_sum_af

    # Fraction of carbon moles to all moles (mole fraction C).
    c_f = np.float32(c_af / total_af)

    # Mole fraction of each element (excluding Carbon and Iron)
    x_vect[1:-1] = x_vect[1:-1] / total_af

    tzero = tzero2(c)  # Using wt% C
    temp = tzero  # starting point for evaluation

    # TODO: This can be declared dynamically
    a_vect = np.zeros(20, dtype=np.float32)
    # Initialise before next while loop, just to get it going
    z = np.float32(1.0)
    # Counter to determine and exit if non convergence occurs
    ctr = 0

    # initialise some other variables
    g = np.float32(0.0)
    tt = np.float32(0.0)

    while z > 0.5:
        # G: Gibbs free energy change for ferrite/austenite transformation
        # for iron (cal/mol). no alloying elements
        # GC: Molar free energy change for ferrite/austenite transformation
        # for carbon (cal/mol). (Li thesis p.146)
        if temp > 0:
            g, temp = dg_fit(temp)
        else:
            # logger.error("Negative temperature determined for Ae3.")
            print("Negative temperature determined for Ae3.")

        g_c = np.float32(-15323 + 7.686 * temp)

        # =910 C (this is the limit for pure Iron transition)
        if temp > 1183:
            # Valid up to 1360K
            # H is the DeltaH (Enthalpy) ferrite-austenite transformation for
            # Iron (Cal/mol)
            # G is Delta0G0 (Gibbs free energy) ferrite-austenite
            # transformation for Iron (Cal/mol)
            h = np.float32(
                2549.0 - 2.746 * temp + 0.0006503 * math.pow(temp, 2)
            )
            g = np.float32(
                2476.0 - 5.03 * temp + 0.003363 * math.pow(temp, 2) -
                0.000000744 * math.pow(temp, 3)
            )
        else:
            # Linear fit 'Delta H' fit of DeltaH (Table V) values (
            # ferrite-austenite transformation for Iron). Kaufman et.al.
            # "Refractory Materials" vol.4, 19, 1970
            h, temp = dh_fit(temp)

        _sum = np.float32(0.0)

        # ETA2 (Li thesis data) references array defined elements for ferrite
        # (alpha) interaction coefficients with carbon in accordance with
        # SimCCT UPDATE B to CALL ETA2Li96(B)
        b_mat = eta2li96()

        # Coefficients for Molar free energy change for SSPT for each element
        # UPDATE E to CALL DGI22(E)
        e_mat = dgi22()

        # Loop ID's below (M) reset for SimCCT array definitions.
        # Note - M in the loop below has to be consistent between elements in
        # 1) mole fraction,
        # 2) "B" &
        # 3) "EE" to work.
        # We are only renumbering for consistency with the SimCCT program to
        # avoid confusion

        # we do 14 loop. runs through each alloying element (1-Mn to 17-P + 2
        # spares 18 & 19)
        for m in range(1, x_vect.shape[0] - 1):
            if x_vect[m] == 0:
                a_vect[m] = 0.0
                ai_vect[m] = 1.0
            else:
                # Calculate the influence of the current element at the
                # specified wt% (as mole fraction)
                e_aust1i = np.float32(b_mat[m, 4] + b_mat[m, 5] / temp)
                e_aust11 = np.float32(8910 / temp)  # Bhadeshia code

                if m == 1:
                    # Data from Gilmour et.al., met. trans., 1972
                    gi = np.float32(
                        6.118 * temp - 7808.0
                    )  # special set for Mn
                else:
                    gi = np.float32(
                        e_mat[m, 1] + (
                            e_mat[m, 2] + e_mat[m, 3] * temp +
                            e_mat[m, 4] * math.log(temp)
                        ) * temp
                    )

                # CALCULATION For SOLUTE PARTITION interaction COEFFICIENT H:
                # 'Delta H' (enthalpy difference) values for BCC to FCC
                # transformation in Iron. table V (2nd last column) by
                # Kaufman "Refractory Materials" vol.4, 19, 1970 H1: enthalpy
                # change (Delta H) for carbon corresponding to the change in
                # free energy (Delta G1)

                # Origin of H1 value in Kirkaldy, Baganis 1978 ([15] =-64,
                # 111 J/mol needs conversion to cal/mol as used here)!
                H1 = np.float32(-15310.0)

                # Using Li data
                e_alpha1i = np.float32(b_mat[m, 1] + b_mat[m, 2] / temp)
                e_alpha11 = np.float32(4.786 + 5066 / temp)

                # Update the value at ai_vect[m]
                ai_vect[m] = ai_eqn3(
                    t0=tzero,
                    dg_n=gi,
                    dg_c=g_c,
                    dg_fe=g,
                    dh_c=H1,
                    dh_fe=h,
                    eta1n_up=e_aust1i,
                    eta11_up=e_aust11,
                    eta1n_down=e_alpha1i,
                    eta11_down=e_alpha11,
                    x1_up=c_f,
                    x1_down=c_f
                )

                # Internal sum for all alloy elements according to eqn (3)
                _sum = _sum + x_vect[m] * ai_vect[m]

        # Puts together all the terms to solve eqn (3) in "Sugden and
        # Bhadeshia, 1989, Mat Sci Tech, Vol.5 p.978"
        delta_t = np.float32(_sum * R * math.pow(tzero, 2))
        temp = tzero + delta_t
        z = tt - temp
        z = abs(z)

        if ctr > 100:
            temp = (tt + temp) / 2
            # break out as not converging
            break

        tt = temp
        ctr = ctr + 1
        # Minimising Z
    return temp, tzero  # Set return value for current Carbon


def convert_wt_2_mol(wt: np.ndarray) -> (np.ndarray, np.array):
    """Finds the mole fractions of each element.

    Args:
        wt: weight % of each element in alloy composition

    Returns:
        c: mole fractions of each element with respect to the complete alloy
           composition (all elements).
        y: mole fraction of each element in relation to Fe only
    """
    d_vect = np.zeros(wt.shape[0], dtype=np.float32)

    # Convert wt% to moles as if 100grams total

    # We MUST ensure that 'C' is always first and 'Fe' is always last.
    # add all the wt% to find total wt% alloying elements
    # note: ensure last one with index -1 is Iron, Fe
    d_vect[-1] = np.sum(wt['weight'][1:11]).item()
    d_vect[-1] = 100.0 - d_vect[-1]  # find wt% Fe by difference
    d_vect[-1] = d_vect[-1] / 55.84  # Fe, calculate moles Fe if 100 g of alloy

    d_vect[0] = (
        wt['weight'][wt['symbol'] == PT.C.name].item() / PT.C.value.atomic_mass
    )

    # 2019-08-04: Update by andrew@neuraldev.io
    # In the original algorithm, Dr. Bendeich hard codes the elements and uses
    # the hard coded atomic mass value for the compositions array.
    # In this version, we only need to ensure the first element is 'C' and the
    # last element is 'Fe' in the array. Once we know that, it doesn't matter
    # what other elements there are as this loop will use a Periodic Table
    # Enum and the Hash Dict access of the atomic mass to calculate the
    # combined weight % of the alloying elements.
    for i, el in enumerate(wt[1:-1], start=1):
        d_vect[i] = el['weight'].item() / PT[el['symbol']].value.atomic_mass

    b1 = np.sum(d_vect).astype(np.float32).item()

    # calculate mole fraction of each element with respect to the complete
    # alloy composition (all elements)
    c_vect = d_vect / b1

    # calculate the mole fraction of each element in relation to Fe only
    y_vect = c_vect / c_vect[-1]  # Fe is always the last element
    y_vect[-1] = 0.0

    return c_vect, y_vect


def tzero2(wt_c: float) -> np.float:
    """Returns pure iron t0 value with specified carbon wt %."""
    # in C
    return np.float32(1115 - 154 * wt_c + 17.5 * math.pow((1.2 - wt_c), 7.5))


def dg_fit(t: float) -> (float, float):
    # Linear fits between 'Delta G' (Gibbs free energy change) values in
    # table V (last column) by Kaufman "Refractory Materials" vol.4, 19,
    # 1970. Data for BCC (alpha) -> FCC (gamma) Iron
    dg_matrix = np.zeros((100, 3), dtype=np.float32)
    # set initial temperature as 0 K (at 20 K in each interval)
    tdh = 300

    dg_matrix[0, 0] = 0
    dg_matrix[1, 0] = 100
    dg_matrix[2, 0] = 200

    # FIXME(andrew@neuraldev.io): This could be done more efficiently
    for i in range(3, 48):
        dg_matrix[i, 0] = tdh
        tdh = tdh + 20

    assert tdh >= 1200, "[ERROR] TDH: {}".format(tdh)

    dg_matrix[48, 0] = 1183

    # Set values for DG
    dg_matrix[0, 1] = 1303
    dg_matrix[1, 1] = 1297
    dg_matrix[2, 1] = 1297
    dg_matrix[3, 1] = 1085
    dg_matrix[4, 1] = 1043
    dg_matrix[5, 1] = 1021
    dg_matrix[6, 1] = 990
    dg_matrix[7, 1] = 956
    dg_matrix[8, 1] = 921
    dg_matrix[9, 1] = 888
    dg_matrix[10, 1] = 855
    dg_matrix[11, 1] = 819
    dg_matrix[12, 1] = 784
    dg_matrix[13, 1] = 749
    dg_matrix[14, 1] = 706
    dg_matrix[15, 1] = 681
    dg_matrix[16, 1] = 649
    dg_matrix[17, 1] = 619
    dg_matrix[18, 1] = 586
    dg_matrix[19, 1] = 553
    dg_matrix[20, 1] = 517
    dg_matrix[21, 1] = 491
    dg_matrix[22, 1] = 462
    dg_matrix[23, 1] = 424
    dg_matrix[24, 1] = 400
    dg_matrix[25, 1] = 375
    dg_matrix[26, 1] = 342
    dg_matrix[27, 1] = 322
    dg_matrix[28, 1] = 283
    dg_matrix[29, 1] = 258
    dg_matrix[30, 1] = 233
    dg_matrix[31, 1] = 205
    dg_matrix[32, 1] = 183
    dg_matrix[33, 1] = 165
    dg_matrix[34, 1] = 142
    dg_matrix[35, 1] = 120
    dg_matrix[36, 1] = 105
    dg_matrix[37, 1] = 89
    dg_matrix[38, 1] = 76
    dg_matrix[39, 1] = 63
    dg_matrix[40, 1] = 50
    dg_matrix[41, 1] = 39
    dg_matrix[42, 1] = 29
    dg_matrix[43, 1] = 20
    dg_matrix[44, 1] = 13
    dg_matrix[45, 1] = 8
    dg_matrix[46, 1] = 4
    dg_matrix[47, 1] = 1
    dg_matrix[48, 1] = 0

    # Find which two array points the current temperature fits and fit the DH
    # value with the linear fit routine. Search the 0 series (temperature) of
    # the array to find when T is < the table value.
    j = 0
    for jj in range(0, 49):
        j = jj
        if t < dg_matrix[jj, 0]:
            break
    # Now we know T fits between i-1 and i

    dg = linear_fit(
        t, dg_matrix[j - 1, 0], dg_matrix[j - 1, 1], dg_matrix[j, 0],
        dg_matrix[j, 1]
    )

    if t > dg_matrix[48, 0]:
        dg = dg_matrix[48, 1]  # cap on value at end of the table data

    return dg, t


def dh_fit(t: float) -> (float, float):
    # linear fits between 'Delta H' (enthalpy difference) values in table V (
    # 2nd last column) by Kaufman "Refractory Materials" vol.4, 19,
    # 1970. Data for BCC (alpha) -> FCC (gamma) Iron
    dh_matrix = np.zeros((100, 3), dtype=np.float32)
    # Set initial temperature as 0 K (at 20 K in each interval)
    _tdh = 300
    dh_matrix[0, 0] = 0
    dh_matrix[1, 0] = 100
    dh_matrix[2, 0] = 200

    # TODO(andrew@neuraldev.io): this could be done more efficiently
    for i in range(3, 48):
        dh_matrix[i, 0] = _tdh
        _tdh = _tdh + 20

    dh_matrix[48, 0] = 1183

    dh_matrix[0, 1] = 1303
    dh_matrix[1, 1] = 1325
    dh_matrix[2, 1] = 1451
    dh_matrix[3, 1] = 1551
    dh_matrix[4, 1] = 1567
    dh_matrix[5, 1] = 1578
    dh_matrix[6, 1] = 1587
    dh_matrix[7, 1] = 1595
    dh_matrix[8, 1] = 1603
    dh_matrix[9, 1] = 1607
    dh_matrix[10, 1] = 1609
    dh_matrix[11, 1] = 1611
    dh_matrix[12, 1] = 1610
    dh_matrix[13, 1] = 1609
    dh_matrix[14, 1] = 1604
    dh_matrix[15, 1] = 1600
    dh_matrix[16, 1] = 1592
    dh_matrix[17, 1] = 1584
    dh_matrix[18, 1] = 1574
    dh_matrix[19, 1] = 1562
    dh_matrix[20, 1] = 1550
    dh_matrix[21, 1] = 1533
    dh_matrix[22, 1] = 1516
    dh_matrix[23, 1] = 1500
    dh_matrix[24, 1] = 1478
    dh_matrix[25, 1] = 1454
    dh_matrix[26, 1] = 1430
    dh_matrix[27, 1] = 1401
    dh_matrix[28, 1] = 1374
    dh_matrix[29, 1] = 1343
    dh_matrix[30, 1] = 1308
    dh_matrix[31, 1] = 1271
    dh_matrix[32, 1] = 1229
    dh_matrix[33, 1] = 1182
    dh_matrix[34, 1] = 1131
    dh_matrix[35, 1] = 1061
    dh_matrix[36, 1] = 999
    dh_matrix[37, 1] = 918
    dh_matrix[38, 1] = 811
    dh_matrix[39, 1] = 699
    dh_matrix[40, 1] = 526
    dh_matrix[41, 1] = 440
    dh_matrix[42, 1] = 387
    dh_matrix[43, 1] = 341
    dh_matrix[44, 1] = 301
    dh_matrix[45, 1] = 268
    dh_matrix[46, 1] = 238
    dh_matrix[47, 1] = 213
    dh_matrix[48, 1] = 210

    # Find which two array points the current temperature fits and fit the DH
    # value with the linear fit routine. Search the 0 series (temperature) of
    # the array to find when T is < the table value
    j = 0
    for jj in range(0, 49):
        j = jj
        if t < dh_matrix[jj, 0]:
            break
    # Now we know T fits between i-1 and i

    dh = linear_fit(
        t, dh_matrix[j - 1, 0], dh_matrix[j - 1, 1], dh_matrix[j, 0],
        dh_matrix[j, 1]
    )

    if t > dh_matrix[48, 0]:
        dh = dh_matrix[48, 1]  # cap on value at end of the table data

    return dh, t


def eta2li96() -> np.ndarray:
    """Set coefficients for the calculation of interaction coefficients for each alloying element with carbon
    (E1i alpha or Delta phase). Values set in Li thesis (p.150, table 3.6, 1st column (E1i(alpha)) values
    referenced to Uhrenius, AIME, 1977, p.28-81

    Key:
    - B_MAT(M, 1): alpha(ferrite) or delta phase coefficients.
    - B_MAT(M, 2): alpha or delta phase coefficients.
    - B_MAT(M, 3): Liquid phase coefficient.
    - B_MAT(M, 4): gamma (austenite) phase coefficients.
    - B_MAT(M, 5): gamma (austenite) phase coefficients.

    Returns:
        A constant numpy.ndarray matrix
    """
    # initiated with all zeroes so if not used already set properly
    b_mat = np.zeros((20, 6), dtype=np.float32)

    # These are from tables in papers.

    # Mn - Li96
    b_mat[1, 5] = -4811
    b_mat[1, 3] = -5060
    b_mat[1, 1] = 0.464
    b_mat[1, 2] = -4989.0

    # Si - Li96
    b_mat[2, 5] = 14794
    b_mat[2, 3] = 18740
    # note: -0.428 for this term but not in main routine
    b_mat[2, 1] = 0.464
    b_mat[2, 2] = 17049.0

    # Ni - Li96
    b_mat[3, 5] = 5533
    b_mat[3, 3] = 5340
    b_mat[3, 1] = 0.464
    b_mat[3, 2] = 6377.0

    # Cr - Li96
    b_mat[4, 4] = 14.193
    b_mat[4, 5] = -30209
    b_mat[4, 3] = -9500
    b_mat[4, 1] = 2.022
    b_mat[4, 2] = 5316.0

    # Mo - Li96
    b_mat[5, 5] = -10714
    b_mat[5, 3] = -7490
    b_mat[5, 1] = 0.464
    b_mat[5, 2] = -9869.0

    # Co - Bhadeshia, Ae3
    b_mat[6, 1] = 58.9
    b_mat[6, 3] = 3550
    b_mat[6, 4] = 0.0E0
    b_mat[6, 5] = 2800.0

    # Al (no data yet]
    # _b_mat[7, 1:5] = 0

    # Cu -Li96
    b_mat[8, 4] = 6.615
    b_mat[8, 5] = -5533
    b_mat[8, 3] = 7586
    b_mat[8, 1] = 7.08
    b_mat[8, 2] = -4689.0

    # As (no data yet]
    # _b_mat[9, 1:5] = 0

    # Ti (no data yet]
    # _b_mat[10, 1:5] = 0

    # V - Li96
    b_mat[11, 5] = -21650
    b_mat[11, 3] = -30100
    b_mat[11, 1] = 0.464
    b_mat[11, 2] = -20806.0

    # W - Li96
    b_mat[12, 5] = -10342
    b_mat[12, 3] = -12230
    b_mat[12, 1] = 0.464
    b_mat[12, 2] = -2603.0

    # S  (no data yet]
    # _b_mat[13, 1:5] = 0

    # N  (no data yet]
    # _b_mat[14, 1:5] = 0

    # Nb -Li96 & Bhadeshia, Ae3
    b_mat[15, 2] = -28770.0
    b_mat[15, 3] = -46615
    b_mat[15, 5] = -28770.0

    # P and B  (no data yet)
    # _b_mat[16:17, 1:5] = 0

    # Spare (no data yet)
    # _b_mat[18:20, 1:5] = 0

    return b_mat


def dgi22() -> np.ndarray:
    """Data for alloying element free energy changes (DELTA G(I)) [Ferrite-
    Austenite transformation] p.146 in Li thesis for equivalent? (note: Li's
    values give different results)

    Key:
    All coefficients here are for Delta G (Gibbs free energy change) for ferrite
    (alpha) -> Austenite(gamma) transformation in cal/mol
    E[i, 1] = fixed
    E[i, 1] = coeff T
    E[i, 1] = T^2 coeff
    E[i, 1] = coeff log T

    Returns:
        A constant numpy.ndarray matrix
    """
    _ee_mat = np.zeros((20, 5), dtype=np.float32)

    # These are from tables in papers.

    # Mn
    _ee_mat[1, 1] = -26650.0
    _ee_mat[1, 2] = 42.69
    _ee_mat[1, 3] = -0.017

    # Si
    _ee_mat[2, 1] = -5964.0
    _ee_mat[2, 2] = 38.799
    _ee_mat[2, 4] = -4.7244

    # Ni
    _ee_mat[3, 1] = -4545.0
    _ee_mat[3, 2] = 3.233

    # Cr
    _ee_mat[4, 1] = -367.0
    _ee_mat[4, 2] = -4.656
    _ee_mat[4, 4] = 0.6568

    # Mo
    _ee_mat[5, 1] = 565.0
    _ee_mat[5, 2] = 0.15

    # Co -no data
    # _ee_mat[6, 1:4] = 0.0

    # Al -no data
    # _ee_mat[7, 1:4] = 0.0

    # Cu - Bhadeshia & Li 96 thesis p.146 (not really for use here?...
    # doesn't fit eqn?]
    _ee_mat[8, 1] = -25500.0
    _ee_mat[8, 2] = 41.183
    _ee_mat[8, 3] = -0.017
    # -0.17 Bhadeshia, -0.017 Li96
    # _ee_mat[8, 4] = 0.0

    # As -no data
    # _ee_mat[9, 1:4] = 0.0
    # Ti -no data
    # _ee_mat[10, 1:4] = 0.0

    # V
    _ee_mat[11, 1] = -8357.0
    # Bhadeshia code (-], Li96 thesis p.146 (+]
    _ee_mat[11, 2] = 13.8
    _ee_mat[11, 3] = -0.0051

    # W
    _ee_mat[12, 1] = 2500.0
    _ee_mat[12, 2] = 0.15

    # S -no data
    # _ee_mat[13, 1:4] = 0.0
    # N -no data
    # _ee_mat[14, 1:4] = 0.0

    # Nb - minor variations between Bhadeshia & Li96
    _ee_mat[15, 1] = 5139.0
    _ee_mat[15, 2] = -2.892

    # B -no data
    # _ee_mat[16, 1:4] = 0.0
    # P -no data
    # _ee_mat[17, 1:4] = 0.0

    # Spare -no data
    # _ee_mat[18:19, 1:4] = 0.0

    return _ee_mat


def ai_eqn3(
    t0: float, dg_n: float, dg_c: float, dg_fe: float, dh_c: float,
    dh_fe: float, eta1n_up: float, eta11_up: float, eta1n_down: float,
    eta11_down: float, x1_up: float, x1_down: float
) -> np.array:
    """This subroutine evaluates Ai component of equation 3 for each alloying element in the Sugden and
    Bhadeshia paper (1989) on calculating Ae3.

    This method can be used for different phase transitions hence the generic nature of the equations.
    Currently it is being used for the gamma-alpha (austenite-ferrite) transition.

    Args:
        t0:
        dg_n:
        dg_c:
        dg_fe:
        dh_c:
        dh_fe:
        eta1n_up:
        eta11_up:
        eta1n_down:
        eta11_down:
        x1_up:
        x1_down:

    Returns:

    """
    # ======================================================================= #
    # Note: UP denotes the higher temp phase.
    # Note: DOWN denotes the lower temp phase
    # ======================================================================= #

    num_1 = math.exp((dg_c / (R * t0)) + eta11_up * x1_up)
    den_1 = float(1 + eta11_down * x1_down * math.exp(dg_c / (R * t0)))
    a10 = float(num_1 / den_1)  # for carbon only, 1

    # logger.info("num_1: {}, den_1: {}, a10: {}".format(num_1, den_1, a10))

    num_2 = math.exp((dg_n / (R * t0)) + eta1n_up * x1_up)
    den_2 = float(1 + eta1n_down * x1_down * math.exp(dg_c / (R * t0)))
    an0 = float(num_2 / den_2)

    b = float(
        (dg_fe / (R * math.pow(t0, 2))) - (math.pow(x1_up, 2) / 2) *
        (eta11_up - eta11_down * math.pow(a10, 2))
    )

    num_3 = float(
        an0 - (1 + x1_up * (1 - x1_up) *
               (eta1n_up - eta11_down * a10 * an0)) * math.exp(b)
    )
    den_3 = float(
        (x1_up * dh_c * a10 + (1 - x1_up) * dh_fe) * math.exp(b)
    )

    return np.float32(num_3 / den_3)


def ae3_multi_carbon(
        wt: np.ndarray, results: np.ndarray
) -> (np.ndarray, np.ndarray):
    """Range of composition for Carbon.

    Args:
        wt:
        results:

    Returns:

    """
    # (includes wt%Fe, AC(20), by difference)

    # Only passing in the original wt% alloys
    # (note: C and Fe will be overwritten below for each iteration of the main
    # loop)
    # t0 = np.float32(0)  # Ae3 value without alloying elements (just Carbon)
    ai_vect = np.zeros(20, dtype=np.float32)
    c = 0.0  # initiate carbon content as 0.00 %

    # reset wt% carbon in array to zero (this will be iterated below within
    # the main loop)
    wt['weight'][wt['symbol'] == PT.C.name] = 0.0
    # reset wt% Fe (Iron) in array to zero (this will be updated below within
    # the main loop)
    wt['weight'][wt['symbol'] == PT.Fe.name] = 0.0

    # ========= # MAIN LOOP - iterates Carbon from 0.00 to 0.96 wt% # ======== #
    for m in range(0, 98):
        # UPDATE Ae3, T0, AI, wt, C to CALL Ae3SetC(Ae3, T0, AI[], wt[], C)
        ae3, t0 = ae3_set_carbon(ai_vect, wt, c)

        # RESULTS Matrix
        results[m, 0] = c  # Current carbon content, wt%-C
        results[m, 1] = ae3 - 273  # Convert to degrees C, Ae3
        # Ae3 for Iron - carbon with no other alloy elem.
        results[m, 2] = t0 - 273
        # Solute partition interaction coefficient (Mn)
        results[m, 3] = ai_vect[1]
        # Solute partition interaction coefficient (Si)
        results[m, 4] = ai_vect[2]
        # Solute partition interaction coefficient (Ni)
        results[m, 5] = ai_vect[3]

        for i in range(4, wt.shape[0] - 1):  # The rest (not Fe)
            results[i + 2, 5] = ai_vect[i]

        # Update C wt% and repeat
        c = c + 0.01

    # Results passed back for clarity but np.ndarray are updated by reference
    return wt, results
