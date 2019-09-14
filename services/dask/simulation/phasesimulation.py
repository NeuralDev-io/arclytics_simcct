# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# simulations.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Arvy Salazar <@Xaraox>', 'Andrew Che <@codeninja55>']
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.8.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.29'
"""phasesimulation.py: 

This file is the module for the solid-state phase transformation simulation as 
defined by Dr. Bendeich but re-written to conform to Object-Oriented 
programming and with some optimisation and data types more compatible with
a Python scientific programming style..
"""

import enum
from typing import Any
from math import pow, sqrt, log, exp, atan

import numpy as np
import dask.array as da

from simulation.utilities import (
    Method, sort_ccr, ConfigurationError, SimulationError
)
from simulation.simconfiguration import SimConfiguration
from simulation.results import ResultsContainer, DynamicNdarray
# noinspection PyPep8Naming
from simulation.periodic import PeriodicTable as PT
from logger.arc_logger import AppLogger
import dask
from dask.distributed import Client

logger = AppLogger(__name__)


class Phase(enum.Enum):
    F = 1
    P = 2
    B = 3
    M = 4


class PhaseSimulation(object):
    """
    This class encapsulates the methods necessary to calculate CCT and TTT.
    """

    def __init__(self, sim_configs: SimConfiguration = None, debug=False):

        # Connect to Dask Scheduler
        Client()

        if sim_configs is not None:
            if not sim_configs.ae_check:
                raise ConfigurationError(
                    'No Ae1 and Ae3 value has been provided.'
                )

            self.configs = sim_configs
            # We only ever use one of "parent," "weld," or "mix"
            self.comp = sim_configs.comp

            self.start_percent = sim_configs.nuc_start
            self.finish_percent = sim_configs.nuc_finish

            if self.start_percent > 1.0 or self.finish_percent > 1.0:
                # logger.debug("Start or Finish percent must be a fraction.")
                raise ConfigurationError(
                    'Start or Finish percent must be a fraction.'
                )

            self.ms = round(sim_configs.ms_temp)
            # Koistinen and Marburger
            self.ms_rate_param = sim_configs.ms_rate_param
            self.bs = round(sim_configs.bs_temp)
            self.g = sim_configs.grain_size

            self.ae1 = round(sim_configs.ae1)
            self.ae3 = sim_configs.ae3
            self.xfe = sim_configs.xfe

        else:
            raise SimulationError(
                'Need a configurations instance to run simulation.'
            )

        # Use an object of Plots instance to store the plot data
        self.plots_data = ResultsContainer()

        if debug:
            # Used for testing only.
            self.comp = sim_configs.comp.copy()
            self.ms = round(sim_configs.ms_temp)
            self.bs = round(sim_configs.bs_temp)
            self.ae1 = round(sim_configs.ae1)

        # This is used multiple times so we will initialise it once here.
        # Columns: Ferrite=0, Pearlite=1, Bainite=2
        # Kirkaldy:
        # [0,0], [0,1], [0,2] spots for starting precipitation
        # [1,0], [1,1], [1,2] spots for finishing precipitation
        # Li98:
        # [2,0], [2,1], [2,2] spots for starting precipitation
        # [3,0], [3,1], [3,2] spots for finishing precipitation
        self.integral_mat = np.zeros((4, 11), dtype=np.float32)
        self._vol_phantom_frac2(self.integral_mat)

    @dask.delayed
    def _ttt_phase_sim(
            self, start_mat, finish_mat, phase, init_temp_curr, upper_limit
    ):
        # NOTE!!!!!
        #  `i` must always be 1 or 2 because of `integral_mat` positions are
        #  static with the integral denominator reliant by other methods
        #  downstream such as _torr_calc2. Upstream, it is created and element
        #  arranged by `self._vol_phantom_frac2`.
        for i in range(1, 3):
            temp_curr = init_temp_curr
            idx_fn = 0
            while temp_curr < upper_limit:
                torr = self._torr_calc2(
                    phase=phase,
                    tcurr=temp_curr,
                    integral_mat=self.integral_mat,
                    i=i
                )

                if i == 1:
                    start_mat[idx_fn, 0] = torr
                    start_mat[idx_fn, 1] = temp_curr
                else:
                    finish_mat[idx_fn, 0] = torr
                    finish_mat[idx_fn, 1] = temp_curr

                idx_fn = idx_fn + 1
                temp_curr = temp_curr + 1

    def ttt(self) -> Any:
        # Number of rows to store results
        n_rows = 1000

        # Can hold 500 time/temperature points for each phase nucleation
        # and completion. Will be dynamic and double its size as we reach
        # 75% capacity.

        # ========= FERRITE PHASE ========= #
        # Ferrite Curve start and finish
        fcs_mat = DynamicNdarray(shape=(n_rows, 2))
        fcf_mat = DynamicNdarray(shape=(n_rows, 2))
        # fcs_mat = da.zeros(
        #     size=(n_rows, 2), dtype=np.float32, chunks=(1000, 2)
        # )
        # fcf_mat = da.zeros(
        #     size=(n_rows, 2), dtype=np.float32, chunks=(1000, 2)
        # )

        phase_f = self._ttt_phase_sim(
            fcs_mat,
            fcf_mat,
            phase=Phase.F,
            init_temp_curr=(self.bs - 50),
            upper_limit=(self.ae3 - 1),
        )

        # ========= PEARLITE PHASE ========= #
        # Pearlite curve start and finish
        pcs_mat = DynamicNdarray(shape=(n_rows, 2))
        pcf_mat = DynamicNdarray(shape=(n_rows, 2))

        phase_p = self._ttt_phase_sim(
            pcs_mat,
            pcf_mat,
            phase=Phase.P,
            init_temp_curr=(self.bs - 50),
            upper_limit=(self.ae1 - 1)
        )

        # ========= BAINITE PHASE ========= #
        # Bainite curve start and finish
        bcs_mat = DynamicNdarray(shape=(n_rows, 2))
        bcf_mat = DynamicNdarray(shape=(n_rows, 2))

        phase_b = self._ttt_phase_sim(
            bcs_mat,
            bcf_mat,
            phase=Phase.B,
            init_temp_curr=self.ms,
            upper_limit=(self.bs - 1)
        )

        # ========= MARTENSITE ========= #
        # Martensite curve start
        temp_curr = self.ms
        torr = self._torr_calc2(
            phase=Phase.M,
            tcurr=temp_curr,
            integral_mat=self.integral_mat,
            i=1
        )
        # Uses Bainite cutoff time. So uses the Bainite phase as the argument

        # Much faster to just use a static array since this is so small.
        msf_mat = np.array(
            [[0.001, self.ms], [torr, self.ms]], dtype=np.float32
        )

        # These are the old positions to keep to ensure we remember them.
        # msf_mat[0, 0] = 0.001
        # msf_mat[0, 1] = self.ms
        # msf_mat[1, 0] = torr
        # msf_mat[1, 1] = self.ms

        phase_b.compute()
        phase_f.compute()
        phase_p.compute()

        def to_plot_dict(array) -> dict:
            assert array.shape[
                       1] == 2, 'Plot Dictionary Array shape must be (n, 2).'
            return {
                'time': np.trim_zeros(array[:, 0]).tolist(),
                'temp': np.trim_zeros(array[:, 1]).tolist()
            }

        return {
            'ferrite_nucleation': to_plot_dict(fcs_mat),
            'ferrite_completion': to_plot_dict(fcf_mat),
            'pearlite_nucleation': to_plot_dict(pcs_mat),
            'pearlite_completion': to_plot_dict(pcf_mat),
            'bainite_nucleation': to_plot_dict(bcs_mat),
            'bainite_completion': to_plot_dict(bcf_mat),
            'martensite': to_plot_dict(msf_mat)
        }

        # noinspection PyUnboundLocalVariable
        # self.plots_data.set_ttt_plot_data(
        #     ferrite_nucleation=fcs_mat[:, :],
        #     ferrite_completion=fcf_mat[:, :],
        #     pearlite_nucleation=pcs_mat[:, :],
        #     pearlite_completion=pcf_mat[:, :],
        #     bainite_nucleation=bcs_mat[:, :],
        #     bainite_completion=bcf_mat[:, :],
        #     martensite=msf_mat
        # )

    def cct(self) -> None:
        # Can be used for any cooling path new routine to simplify iterative
        # routines using any of the methods coded in. Should be much simpler
        # to code and follow and only needs to be done once not repeated for
        # each method as before

        # The equilibrium phase fraction of ferrite at the eutectic temperature
        # (consistent with Kirkaldy implementation and explained by
        # Watt et. al. 88)
        if self.xfe >= 1.0:
            raise ConfigurationError('XFE has to be below 1.0')

        # The integrals for relevant % transformed at nucleation and completion
        # was initialised and run at instantiation of this instance.

        # Number of rows to store results
        n_rows = 500

        # ========== # TIME LOOP # ========== #
        # The time increments can be
        # either constant cooling rate or follow a defined curve. Figure this
        # out first and populate an array containing discreet increments of
        # time for the FOR loop to follow. The increment size does not have
        # to be constant as some segments can be run through quickly i.e. the
        # cooling from initial temperature to Ae3 only involves potential
        # grain growth

        # Can hold 500 time/temperature points for each phase nucleation
        # and completion. Will be dynamic and double its size as we reach
        # 75% capacity.

        # Ferrite nucleation and completion
        cct_record_f_mat = DynamicNdarray(shape=(n_rows, 2))
        cct_record_f_end_mat = DynamicNdarray(shape=(n_rows, 2))
        # Pearlite nucleation and completion
        cct_record_p_mat = DynamicNdarray(shape=(n_rows, 2))
        cct_record_p_end_mat = DynamicNdarray(shape=(n_rows, 2))
        # Bainite nucleation and completion
        cct_record_b_mat = DynamicNdarray(shape=(n_rows, 2))
        cct_record_b_end_mat = DynamicNdarray(shape=(n_rows, 2))

        # Counters
        idx_f, idx_p, idx_b, idx_m = 0, 0, 0, 0
        idx_f_end, idx_p_end, idx_b_end, idx_m_end = 0, 0, 0, 0

        # Find the critical cooling rates for each phase
        # Storage for critical cooling rates
        ccr_mat = np.zeros((3, 2), dtype=np.float32)
        # CCR[0,0] - ferrite-init, CCR[0,1] - ferrite-finish
        # CCR(1,0] - pearlite-init, CCR[1,1] - pearlite-finish
        # CCR[2,0] - bainite-init, CCR[2,1] - bainite-finish
        self._critical_cooling_rate(ccr_mat, self.integral_mat)
        # Sort Critical cooling rates from lowest to highest
        sorted_ccr = sort_ccr(ccr_mat)

        # Variable for the cooling rate (C/sec) at this point in time.
        # Usually constant for each isotherm but might vary if using a
        # defined cooling path from a table.
        # TODO(andrew@neuraldev.io): Ask Dr. Bendeich if we can make a param
        speedup = 1.2
        # Degrees/sec this starts at the fastest critical cooling rate
        cooling_rate = sorted_ccr[-1] * 2 * speedup
        i_ctr = 3

        # =================================================================== #
        # ===================== # MAIN COOLING RATE LOOP ==================== #
        # =================================================================== #
        for i in range(100):
            cooling_rate = cooling_rate / speedup

            if cooling_rate < sorted_ccr[i_ctr]:
                # set back to the next slowest critical cooling rate identified
                i_ctr = i_ctr - 1

                if i_ctr < 0:
                    i_ctr = 0
                    speedup = 2.0

            # Initialise time at start for each cooling rate
            time = 0.0
            # Initialise temperature at the start point for each cooling rate
            temp_curr = self.configs.temp_peak
            # set the first increment time at 1 degree/increment (this will
            # be controlled within the loop once started)
            increm_time = 1 / cooling_rate

            # Now within fixed Temperature path
            # Reset the nucleation volume fractions to 0.0 for new cooling rate
            nuc_frac_ferrite = 0.0
            nuc_frac_pearlite = 0.0
            nuc_frac_bainite = 0.0
            # Reset the nucleation volume fractions to 0.0 for new cooling rate
            nuc_frac_ferrite_end = 0.0
            nuc_frac_pearlite_end = 0.0
            nuc_frac_bainite_end = 0.0

            # Reset the triggers for the current cooling rate (may not have
            # been tripped on previous cooling rate)
            # Trigger after Ferrite nucleation point has been found to stop
            # the routine recoding for the current cooling rate
            # Ferrite, Pearlite, and Bainite triggers respectively
            stop_f, stop_p, stop_b = False, False, False
            stop_f_end, stop_p_end, stop_b_end = False, False, False

            # ========================= # STAGE 1 # ========================= #
            # If above this temperature, no nucleation of any phase will be
            # occurring, however, grain growth can occur.
            while temp_curr > self.ae3:
                # For the current temperature and time interval find the new
                # grain size (if not fixed) for the moment we will use the
                # fixed grain size self.g
                # Find the new temperature for the next iteration of this loop
                temp_curr = self._next_temp(
                    temp_curr, cooling_rate, increm_time
                )
                time = time + increm_time

            # ========================= # STAGE 2 # =========================
            # Now we are below Ae3 and any phase can occur (unless we
            # subdivide further .... not necessary unless we need to speed
            # the routine up)

            # We want it to drop 1 degree each increment. We need the
            # appropriate time step at the current cooling rate
            increm_time = 1 / cooling_rate  # Slow things down a bit

            # If above the martensite transformation temperature then we are
            # looking for any phase that might occur
            while temp_curr > self.ms:
                # Find the total time to nucleation at the current
                # temperature and divide the current increment time by this
                # to find the fraction consumed in the current step. Then add
                # this to the previous total for the relevant phases when the
                # total is 1.0 nucleation has occurred.

                # =============== # Look for FERRITE START # =============== #
                if not stop_f:
                    torr_f = self._torr_calc2(
                        phase=Phase.F,
                        tcurr=temp_curr,
                        integral_mat=self.integral_mat,
                        i=1
                    )
                    # Add up the cumulative fraction of ferrite converted
                    # toward the nucleation point
                    nuc_frac_ferrite = (
                        nuc_frac_ferrite + (increm_time / torr_f)
                    )

                    if nuc_frac_ferrite > 1.0:
                        cct_record_f_mat[idx_f, 0] = time  # x-axis
                        cct_record_f_mat[idx_f, 1] = temp_curr  # y-axis
                        idx_f = idx_f + 1
                        # trigger to stop recoding for ferrite for current
                        # cooling rate
                        stop_f = True

                # =============== # Look for FERRITE FINISH # =============== #
                if not stop_f_end:
                    torr_f_end = self._torr_calc2(
                        phase=Phase.F,
                        tcurr=temp_curr,
                        integral_mat=self.integral_mat,
                        i=2
                    )
                    nuc_frac_ferrite_end = nuc_frac_ferrite_end + (
                        increm_time / torr_f_end
                    )
                    # Record current point and stop looking for this phase at
                    # current cooling rate.
                    if nuc_frac_ferrite_end > 1.0:
                        cct_record_f_end_mat[idx_f_end, 0] = time
                        cct_record_f_end_mat[idx_f_end, 1] = temp_curr
                        idx_f_end = idx_f_end + 1
                        stop_f_end = True

                # =============== # Look for PEARLITE START # =============== #
                if not stop_p and temp_curr < self.ae1:
                    torr_p = self._torr_calc2(
                        phase=Phase.P,
                        tcurr=temp_curr,
                        integral_mat=self.integral_mat,
                        i=1
                    )
                    # Add up the cumulative fraction of pearlite converted
                    # toward the nucleation point
                    nuc_frac_pearlite = nuc_frac_pearlite + (
                        increm_time / torr_p
                    )

                    if nuc_frac_pearlite > 1.0:
                        cct_record_p_mat[idx_p, 0] = time
                        cct_record_p_mat[idx_p, 1] = temp_curr
                        idx_p = idx_p + 1
                        # trigger to stop recoding for ferrite for current
                        # cooling rate
                        stop_p = True

                # =============== # Look for PEARLITE FINISH # =============== #
                if not stop_p_end and temp_curr < self.ae1:
                    torr_p_end = self._torr_calc2(
                        phase=Phase.P,
                        tcurr=temp_curr,
                        integral_mat=self.integral_mat,
                        i=2
                    )
                    nuc_frac_pearlite_end = nuc_frac_pearlite_end + (
                        increm_time / torr_p_end
                    )

                    if nuc_frac_pearlite_end > 1.0:
                        cct_record_p_end_mat[idx_p_end, 0] = time
                        cct_record_p_end_mat[idx_p_end, 1] = temp_curr
                        idx_p_end = idx_p_end + 1
                        stop_p_end = True

                # =============== # Look for BAINITE START # =============== #
                if not stop_b and temp_curr < self.bs:
                    torr_b = self._torr_calc2(
                        phase=Phase.B,
                        tcurr=temp_curr,
                        integral_mat=self.integral_mat,
                        i=1
                    )
                    # Add up the cumulative fraction of bainite converted
                    # toward the nucleation point
                    nuc_frac_bainite = nuc_frac_bainite + (
                        increm_time / torr_b
                    )

                    if nuc_frac_bainite > 1.0:
                        cct_record_b_mat[idx_b, 0] = time
                        cct_record_b_mat[idx_b, 1] = temp_curr
                        idx_b = idx_b + 1
                        stop_b = True

                # =============== # Look for BAINITE FINISH # =============== #
                if not stop_b_end and temp_curr < self.bs:
                    torr_b_end = self._torr_calc2(
                        phase=Phase.B,
                        tcurr=temp_curr,
                        integral_mat=self.integral_mat,
                        i=2
                    )
                    nuc_frac_bainite_end = nuc_frac_bainite_end + (
                        increm_time / torr_b_end
                    )

                    if nuc_frac_bainite_end > 1.0:
                        cct_record_b_end_mat[idx_b_end, 0] = time
                        cct_record_b_end_mat[idx_b_end, 1] = temp_curr
                        idx_b_end = idx_b_end + 1
                        stop_b_end = True

                # Stopping condition
                # Find the new temperature for the next iteration of this loop
                temp_curr = self._next_temp(
                    temp_curr, cooling_rate, increm_time
                )
                time = time + increm_time

        # ==================== # MARTENSITE # ==================== #
        # Martensite completion
        # Much faster to just make a static `ndarray`
        cct_record_m_mat = np.array(
            [[0.001, self.ms], [cct_record_b_end_mat[0, 0], self.ms]],
            dtype=np.float32
        )
        # These are the old positions to keep to ensure we remember them.
        # cct_record_m_mat[0, 0] = 0.001
        # cct_record_m_mat[0, 1] = self.ms
        # cct_record_m_mat[1, 0] = cct_record_b_end_mat[0, 0]
        # cct_record_m_mat[1, 1] = self.ms

        # No we are below the Martensite temperature and all remaining
        # Austenite will convert to Martensite (unless we have a reheating step
        # before full conversion, however, this is beyond the scope of this
        # project at this point.

        # Store the data in a Results Object
        self.plots_data.set_cct_plot_data(
            ferrite_nucleation=cct_record_f_mat[:(idx_f - 1), :],
            ferrite_completion=cct_record_f_end_mat[:(idx_f_end - 1), :],
            pearlite_nucleation=cct_record_p_mat[:(idx_p - 1), :],
            pearlite_completion=cct_record_p_end_mat[:(idx_p_end - 1), :],
            bainite_nucleation=cct_record_b_mat[:(idx_b - 1), :],
            bainite_completion=cct_record_b_end_mat[:(idx_b_end - 1), :],
            martensite=cct_record_m_mat
        )

    def user_cooling_profile(self) -> None:

        # We first start by doing some setup
        # Define array to hold time and temperature data
        n_rows = 1000
        user_cool_mat = DynamicNdarray(shape=(n_rows, 2))
        # Count will set the array ID for each increment during cooling
        count = 0
        # Get the requested cooling rate
        cooling_rate = self.configs.cct_cooling_rate
        if cooling_rate < 0:
            raise SimulationError("Don't be silly with negative Cooling Rate.")

        # ========== # Setup initial run parameters # ========== #
        time = 0.0
        # initialise temperature at the start point for curve
        temp_curr = self.configs.temp_peak

        # If increment is set too high then the slow cooling rate calculations
        # start to deviate from reality
        if cooling_rate < 1:
            # set the first increment time at 1 degree/increment (this may be
            # controlled within the loop once started)
            increm_time = 0.1 / cooling_rate
        else:
            increm_time = 1 / cooling_rate

        # ========== # Setup for Phase Fraction Monitoring # ========== #
        # Compared to `user_cool_mat` and `phase_vol`, we make these array a
        # little larger so they don't need to be resized.
        n_rows_other = 2000
        # 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite
        phase_frac_mat = DynamicNdarray(shape=(n_rows_other, 5))
        # initiate fraction values (actual % of the phase formed) at time 0
        phase_frac_mat[0, 0] = 1.0  # its all austenite at the start
        # note: Dr. Bendeich sets phase_frac_mat[0, 1:6] to 0 so make sure
        # you always use np.zeros()

        # 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite
        # initiate nucleation ratios values (proportion of nucleation time
        # completed) at time 0
        phase_nuc_ratio = DynamicNdarray(shape=(n_rows_other, 5))
        # note: Dr. Bendeich sets phase_nuc_ratio[0, 1:6] to 0 so make sure
        # you always use np.zeros()

        # 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite
        # initiate completion ratios values (proportion of nucleation time
        # completed) at time 0
        phase_complete_ratio = DynamicNdarray(shape=(n_rows_other, 5))
        # note: Dr. Bendeich sets phase_complete_ratio[0, 1:6] to 0 so make sure
        # you always use np.zeros()

        # 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite
        # Initiate fraction values (actual % of the phase formed) at time 0
        # would by default be phase_vol[0, 0:5] = 0 since we use np.zeros()
        # NOTE: THIS IS THE PIE CHART DATA
        phase_vol = DynamicNdarray(shape=(n_rows, 5))
        phase_vol[0, 0] = 100.0  # Austenite
        # note: Dr. Bendeich sets phase_vol[0, 1:6] to 0 so make sure
        # you always use np.zeros()

        if self.xfe >= 1.0:
            raise ConfigurationError('XFE has to be below 1.0')

        # The integrals for relevant % transformed at nucleation and completion
        # was initialised and run at instantiation of this instance.

        # = # Set loop for all time intervals until cooling is finished # = #

        # Modified for new Martensite transformation method (Koistinen and
        # Marburger)
        # MS - 20 : run down to current Martensite temp. (MS) - 20 deg.C
        # note: temp_curr is cooling, i.e. going down from temp_peak
        while temp_curr > 20:
            # record current temperature and time in storage array
            user_cool_mat[count, 0] = time
            user_cool_mat[count, 1] = temp_curr

            # This is the Phase transformation bit
            if count > 0:
                # first time through everything is at zero and pre set for
                # this point
                self._transform_inc(
                    tcurr=temp_curr,
                    inc_time=increm_time,
                    phase_n_ratio=phase_nuc_ratio,
                    phase_c_ratio=phase_complete_ratio,
                    phase_frac=phase_frac_mat,
                    phase_vol=phase_vol,
                    integral_mat=self.integral_mat,
                    cnt=count
                )

            count = count + 1
            # Find the new temperature for the next iteration of this loop
            temp_curr = self._next_temp(temp_curr, cooling_rate, increm_time)
            time = time + increm_time

        # Trim the user cool curve to the max count it reaches
        n_max = count - 1
        user_cool_mat = user_cool_mat[:n_max, :]
        # Store the data in a Results Object
        # phase_vol: 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite
        # phase_vol.shape = (n,5)
        self.plots_data.set_user_cool_plot_data(
            user_cooling_curve=user_cool_mat,
            user_phase_fraction_data=phase_vol[:n_max, :],
            slider_time_field=user_cool_mat[-1, 0],
            slider_temp_field=user_cool_mat[-1, 1],
            slider_max=n_max - 1,
        )

    @staticmethod
    def _sigmoid2(x) -> float:
        return float(1 / (pow(x, (0.4 * (1 - x))) * pow((1 - x), (0.4 * x))))

    @staticmethod
    def _imoid(x) -> float:
        """Kirkaldy 1983 method I(X)."""
        return float(
            1 / (pow(x, (2.0 * (1 - x) / 3)) * pow((1 - x), (2.0 * x / 3)))
        )

    def _imoid_prime2(self, x: float) -> float:
        """This is the specific Kirkaldy implementation for I(X) used in the
        "sluggish" Kinetic Bainite reaction rate. """
        c = self.comp['weight'][self.comp['symbol'] == PT.C.name][0]
        ni = self.comp['weight'][self.comp['symbol'] == PT.Ni.name][0]
        cr = self.comp['weight'][self.comp['symbol'] == PT.Cr.name][0]
        mo = self.comp['weight'][self.comp['symbol'] == PT.Mo.name][0]
        mn = self.comp['weight'][self.comp['symbol'] == PT.Mn.name][0]

        numerator = float(
            exp(
                pow(x, 2) * (
                    (1.9 * c) + (2.5 * mn) + (0.9 * ni) + (1.7 * cr) +
                    (4.0 * mo) - 2.6
                )
            )
        )

        b = (1.9 * c) + (2.5 * mn) + (0.9 * ni) + (1.7 * cr) + (4.0 * mo) - 2.6

        if b < 0:
            return (
                1 / (
                    pow(x,
                        (2.0 * (1 - x) / 3.0)) * pow((1 - x), (2.0 * x / 3.0))
                )
            )

        return (
            numerator /
            (pow(x, (2.0 * (1 - x) / 3.0)) * pow((1 - x), (2.0 * x / 3.0)))
        )

    @staticmethod
    def _get_sx_integral(x) -> float:
        if (x >= 0.00) and (x < 0.01):
            return 1.7635 * x**0.6118
        if (x >= 0.01) and (x < 0.5):
            return 1.5401 * x**0.5846
        if (x >= 0.5) and (x < 0.95):
            return 1.4 * x**2 - 0.45 * x + 0.936
        if (x >= 0.95) and (x <= 1.0):
            return 2383.21 * x**3 - 6891.57 * x**2 + 6646 * x - 2135.57

    # noinspection PyUnusedLocal,SpellCheckingInspection
    def _de_integrator(self, i, a, b, eps, err, nn, method) -> float:
        """Double Exponential Transformation.

        Args:
            i:
            a:
            b:
            eps:
            err:
            nn:
            method:

        Returns:

        """
        n = 0
        # Adjustable parameters
        mmax = 256
        efs = 0.1
        hoff = 8.5
        # ======================================== #
        pi2 = 2 * atan(1.0)
        epsln = 1 - log(efs * eps)
        epsh = sqrt(efs * eps)
        h0 = hoff / epsln
        ehp = exp(h0)
        ehm = 1 / ehp
        epst = exp(-ehm * epsln)
        ba = b - a
        ir = 0.0
        fa = 0.0
        fb = 0.0

        if method == 1:
            ir = self._sigmoid2((a + b) * 0.5) * (ba * 0.25)
        elif method == 2:
            ir = self._imoid((a + b) * 0.5) * (ba * 0.25)
        elif method == 3:
            ir = self._imoid_prime2((a + b) * 0.5) * (ba * 0.25)
        n = n + 1

        i = ir * (2 * pi2)
        err = abs(i) * epst
        h = 2 * h0
        m = 1
        errh = 0.0

        while True:
            iback = i
            irback = ir
            t = h * 0.5
            while True:
                em = exp(t)
                ep = pi2 * em
                em = pi2 / em
                while True:
                    xw = 1 / (1 + exp(ep - em))
                    xa = ba * xw
                    wg = xa * (1 - xw)

                    if method == 1:
                        fa = self._sigmoid2(a + xa) * wg
                        fb = self._sigmoid2(b - xa) * wg
                    elif method == 2:
                        fa = self._imoid(a + xa) * wg
                        fb = self._imoid(b - xa) * wg
                    elif method == 3:
                        fa = self._imoid_prime2(a + xa) * wg
                        fb = self._imoid_prime2(b - xa) * wg
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
            if m == 1:
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

    def _vol_phantom_frac2(self, integrated_mat) -> None:
        """This routine will return the expected volume or phantom fraction for
        the specific methodology being requested by the USER defined
        precipitation points for starting and finishing.

        xfe: equilibrium phase fraction of ferrite.
        xbr: remaining volume available for transformation to Bainite. Will
             be = 1.0 for TTT but may be lower in CCT if Ferrite and Pearlite
             have already formed.

        nuc_start: the requested start %. usually 1.0% or 0.1% (converted to a
                   fraction i.e. 0.01 or 0.001 respectively).
        nuc_finish: the requested end %. usually 99.9% (converted to a
                    fraction. i.e. 0.999)

        Definitions of "integrated_mat[,]"
        Kirkaldy:
        [0,0], [0,1], [0,2]: spots for starting precipitation of F, P, and B
        respectively.
        [1,0], [1,1], [1,2]: spots for finishing precipitation of F, P, and B
        respectively.

        Li98:
        [2,0], [2,1], [2,2]: spots for starting precipitation of F, P, and B
        respectively
        [3,0], [3,1], [3,2]: spots for finishing precipitation of F, P, and B
        respectively

        Args:
            integrated_mat: definition above.

        Returns:
            None. integrated_mat is updated by reference.
        """
        err = None
        nn = None

        # This is used multiple times so we will initialise it once here.
        # Columns: Ferrite=0, Pearlite=1, Bainite=2
        # Kirkaldy:
        # [0,0], [0,1], [0,2] spots for starting precipitation
        # [1,0], [1,1], [1,2] spots for finishing precipitation
        # Li98:
        # [2,0], [2,1], [2,2] spots for starting precipitation
        # [3,0], [3,1], [3,2] spots for finishing precipitation

        if self.configs.method == Method.Li98:

            # FERRITE START
            xf = self.start_percent * self.xfe

            integrated_mat[2, 5] = xf

            sig_int_ferrite = 0
            sig_int_ferrite = self._de_integrator(
                sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 1
            )
            integrated_mat[2, 0] = sig_int_ferrite

            # PEARLITE START xpe = 1.0 - self.xfe CheckPhantomTestP.Checked
            # is always false because it is by default false and invisible
            xp = self.start_percent / (1 - self.xfe)
            integrated_mat[2, 6] = xp

            sig_int_pearlite, sig_int_pearlite_t = 0, 0
            sig_int_pearlite = self._de_integrator(
                sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 1
            )
            integrated_mat[2, 1] = sig_int_pearlite

            xb = self.start_percent

            integrated_mat[2, 7] = xb
            sig_int_bainite = 0
            sig_int_bainite = self._de_integrator(
                sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 1
            )
            integrated_mat[2, 2] = sig_int_bainite

            # =============================================================== #

            # FERRITE FINISH
            xf = self.finish_percent * self.xfe
            if xf > 1.0:
                xf = 0.9999999

            # TODO(andrew@neuraldev.io): Figure out why there is a division by
            #  Zero error at this point always.
            sig_int_ferrite = self._de_integrator(
                sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 1
            )
            integrated_mat[3, 0] = sig_int_ferrite

            # PEARLITE FINISH
            xp = self.finish_percent / (1 - self.xfe)
            if xp >= 1.0:
                xp = 0.9999999

            sig_int_pearlite = self._de_integrator(
                sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 1
            )
            integrated_mat[3, 1] = sig_int_pearlite

            # BAINITE
            xb = self.finish_percent
            if xb >= 1.0:
                xb = 0.9999999

            sig_int_bainite = self._de_integrator(
                sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 1
            )
            integrated_mat[3, 2] = sig_int_bainite

        elif self.configs.method == Method.Kirkaldy83:
            # FERRITE START
            xf = self.start_percent / self.xfe
            sig_int_ferrite = 0
            sig_int_ferrite = self._de_integrator(
                sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2
            )
            integrated_mat[0, 0] = sig_int_ferrite

            # PEARLITE START
            xp = self.start_percent / (1 - self.xfe)
            sig_int_pearlite = 0
            sig_int_pearlite = self._de_integrator(
                sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 2
            )
            integrated_mat[0, 1] = sig_int_pearlite

            # BAINITE START
            xb = self.start_percent
            sig_int_bainite = 0
            sig_int_bainite = self._de_integrator(
                sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3
            )
            integrated_mat[0, 2] = sig_int_bainite

            # FERRITE FINISH
            xf = self.finish_percent * self.xfe
            sig_int_ferrite = 0
            sig_int_ferrite = self._de_integrator(
                sig_int_ferrite, 0.0, xf, 0.000000000000001, err, nn, 2
            )
            integrated_mat[1, 0] = sig_int_ferrite

            # PEARLITE FINISH
            xp = self.finish_percent * (1 - self.xfe)
            if xp >= 1.0:
                xp = 0.9999999
            sig_int_pearlite = 0
            sig_int_pearlite = self._de_integrator(
                sig_int_pearlite, 0.0, xp, 0.000000000000001, err, nn, 2
            )
            integrated_mat[1, 1] = sig_int_pearlite

            # BAINITE FINISH
            xb = self.finish_percent
            if xb >= 1.0:
                xb = 0.9999999
            sig_int_bainite = 0
            sig_int_bainite = self._de_integrator(
                sig_int_bainite, 0.0, xb, 0.000000000000001, err, nn, 3
            )
            integrated_mat[1, 2] = sig_int_bainite

    def _torr_calc2(
        self, phase: Phase, tcurr: float, integral_mat: np.ndarray, i: int
    ) -> float:
        r_gas = 1.985

        wt = self.comp
        c = wt['weight'][wt['symbol'] == PT.C.name][0]
        mn = wt['weight'][wt['symbol'] == PT.Mn.name][0]
        si = wt['weight'][wt['symbol'] == PT.Si.name][0]
        mo = wt['weight'][wt['symbol'] == PT.Mo.name][0]
        ni = wt['weight'][wt['symbol'] == PT.Ni.name][0]
        cr = wt['weight'][wt['symbol'] == PT.Cr.name][0]

        # This is used multiple times so we will initialise it once here.
        # Columns: Ferrite=0, Pearlite=1, Bainite=2
        # Kirkaldy:
        # [0,0], [0,1], [0,2] spots for starting precipitation
        # [1,0], [1,1], [1,2] spots for finishing precipitation
        # Li98:
        # [2,0], [2,1], [2,2] spots for starting precipitation
        # [3,0], [3,1], [3,2] spots for finishing precipitation

        if self.configs.method == Method.Li98:
            sint_f = integral_mat[i + 1, 0]
            sint_p = integral_mat[i + 1, 1]
            sint_b = integral_mat[i + 1, 2]

            if phase == Phase.F:
                fc = float(
                    exp(
                        1.0 + (6.31 * c) + (1.78 * mn) + (0.31 * si) +
                        (1.12 * ni) + (2.7 * cr) + (4.06 * mo)
                    )
                )

                return float(
                    fc / (
                        pow(2, (0.41 * self.g)) * pow((self.ae3 - tcurr), 3) *
                        exp(-27500 / (r_gas * (tcurr + 273)))
                    ) * sint_f
                )

            elif phase == Phase.P:
                pc = float(
                    exp(
                        -4.25 + (4.12 * c) + (4.36 * mn) + (0.44 * si) +
                        (1.71 * ni) + (3.33 * cr) + (5.19 * sqrt(mo))
                    )
                )

                return float(
                    pc / (
                        pow(2, (0.32 * self.g)) * pow((self.ae1 - tcurr), 3) *
                        exp(-27500 / (r_gas * (tcurr + 273)))
                    ) * sint_p
                )

            elif phase == Phase.B or phase == Phase.M:
                bc = float(
                    exp(
                        -10.23 + (10.18 * c) + (0.85 * mn) + (0.55 * ni) +
                        (0.9 * cr) + (0.36 * mo)
                    )
                )

                return float(
                    bc / (
                        pow(2, (0.29 * self.g)) * pow((self.bs - tcurr), 2) *
                        exp(-27500 / (r_gas * (tcurr + 273)))
                    ) * sint_b
                )

        elif self.configs.method == Method.Kirkaldy83:
            iint_f = integral_mat[i - 1, 0]
            iint_p = integral_mat[i - 1, 1]
            iint_b = integral_mat[i - 1, 2]

            if phase == Phase.F:
                fc = float(
                    ((59.6 * mn) + (1.45 * ni) + (67.7 * cr) + (244 * mo))
                )

                return float(
                    fc / (
                        2**((self.g - 1) / 2) * ((self.ae3 - tcurr)**3) *
                        exp(-23500 / (r_gas * (tcurr + 273)))
                    ) * iint_f
                )

            elif phase == Phase.P:
                pc = float(1.79 + 5.42 * (cr + mo + 4 * mo * ni))
                dinv = float(
                    (1 / exp(-27500 / (r_gas * (tcurr + 273)))) + (
                        (0.01 * cr + 0.52 * mo) /
                        exp(-37500 / (r_gas * (tcurr + 273)))
                    )
                )

                return float(
                    pc / (
                        (
                            2**((self.g - 1) / 2) * ((self.ae1 - tcurr)**3) *
                            (1 / dinv)
                        ) * iint_p
                    )
                )

            elif phase == Phase.B or phase == Phase.M:
                bc = float(
                    (2.34 + (10.1 * c) + (3.8 * cr) + (19.0 * mo)) *
                    pow(10, -4)
                )

                return float(
                    bc / (
                        2**((self.g - 1) / 2) * ((self.bs - tcurr)**2) *
                        exp(-27500 / (r_gas * (tcurr + 273)))
                    ) * iint_b
                )

        return -1.0

    def _critical_cooling_rate(
        self, ccr_mat: np.ndarray, integral2: np.ndarray
    ) -> None:
        """Find the critical cooling rate for each phase.

        Args:
            ccr_mat: The `numpy.ndarray` to update with the critical cooling
                     rate for each phone
            integral2: The `numpy.ndarray` Rank-2 array with the integrals for
                       each phase.

        Returns:
            None
        """

        # ========================================================= #
        # ==================== # BAINITE CCR # ==================== #
        # ========================================================= #
        torr_b, ccr_bcs, ccr_bcf = 0.0, 0.0, 0.0
        time_accumulate = 0
        # initialise the time interval for this loop
        time_interval = 1.0
        # Start at Martensite temperature and work up to Bainite limit
        temp_curr = self.ms

        # FIXME: This while loop can be put out to a helper function with:
        #  - i.e. bs is limit
        #  - return time_accumulate, ccr
        while temp_curr < self.bs:
            # Get isothermal nucleation time at current temperature
            torr_b = self._torr_calc2(
                phase=Phase.B, tcurr=temp_curr, integral_mat=integral2, i=1
            )

            # Bainite start. Accumulation ratio
            ccr_bcs = ccr_bcs + (time_interval / torr_b)
            temp_curr = temp_curr + 1
            time_accumulate = time_accumulate + time_interval

        ccr_mat[2, 0] = ccr_bcs / (
            (self.bs - self.ms) / (time_accumulate - time_interval)
        )

        # Reset and run to full transformation
        time_accumulate = 0

        # Start at Martensite temperature and work up to Bainite limit
        temp_curr = self.ms

        while temp_curr < self.bs:
            # Get isothermal nucleation time at current temperature
            torr_b = self._torr_calc2(
                phase=Phase.B, tcurr=temp_curr, integral_mat=integral2, i=2
            )
            # Bainite finish. Accumulation ratio
            ccr_bcf = ccr_bcf + (time_interval / torr_b)
            temp_curr = temp_curr + 1.0
            time_accumulate = time_accumulate + time_interval

        ccr_mat[2, 1] = ccr_bcf / (
            (self.bs - self.ms) / (time_accumulate - time_interval)
        )

        # ========================================================== #
        # ==================== # PEARLITE CCR # ==================== #
        # ========================================================== #
        torr_p, ccr_pcs, ccr_pcf = 0.0, 0.0, 0.0
        time_accumulate = 0
        temp_curr = self.bs

        while temp_curr < self.ae1:
            torr_p = self._torr_calc2(
                phase=Phase.P, tcurr=temp_curr, integral_mat=integral2, i=1
            )
            # Pearlite start. Accumulation ratio
            ccr_pcs = ccr_pcs + (time_interval / torr_p)
            temp_curr = temp_curr + 1.0
            time_accumulate = time_accumulate + time_interval

        ccr_mat[1, 0] = ccr_pcs / (
            (self.ae1 - self.bs) / (time_accumulate - time_interval)
        )

        # Reset and run to full transformation
        time_accumulate = 0
        # Start at Martensite temperature and work up to Bainite limit
        temp_curr = self.bs

        while temp_curr < self.ae1:
            torr_p = self._torr_calc2(
                phase=Phase.P, tcurr=temp_curr, integral_mat=integral2, i=1
            )
            # Pearlite start. Accumulation ratio
            ccr_pcf = ccr_pcf + (time_interval / torr_p)
            temp_curr = temp_curr + 1
            time_accumulate = time_accumulate + time_interval

        ccr_mat[1, 1] = ccr_pcf / (
            (self.ae1 - self.bs) / (time_accumulate - time_interval)
        )

        # ========================================================= #
        # ==================== # FERRITE CCR # ==================== #
        # ========================================================= #
        torr_f, ccr_fcs, ccr_fcf = 0.0, 0.0, 0.0
        time_accumulate = 0

        # Start at Bainite temperature and work up to Bainite limit
        temp_curr = self.bs

        while temp_curr < self.ae3:
            torr_f = self._torr_calc2(
                phase=Phase.F, tcurr=temp_curr, integral_mat=integral2, i=1
            )
            # Ferrite start. Accumulation ratio
            ccr_fcs = ccr_fcs + (time_interval / torr_f)
            temp_curr = temp_curr + 1
            time_accumulate = time_accumulate + time_interval

        ccr_mat[0, 0] = ccr_fcs / (
            (self.ae3 - self.bs) / (time_accumulate - time_interval)
        )

        # Reset and run to full transformation
        time_accumulate = 0
        # Start at Martensite temperature and work up to Bainite limit
        temp_curr = self.bs

        while temp_curr < self.ae3:
            torr_f = self._torr_calc2(
                phase=Phase.F, tcurr=temp_curr, integral_mat=integral2, i=1
            )
            ccr_fcf = ccr_fcf + (time_interval / torr_f)
            temp_curr = temp_curr + 1
            time_accumulate = time_accumulate + time_interval

        ccr_mat[0, 1] = ccr_fcf / (
            (self.ae3 - self.bs) / (time_accumulate - time_interval)
        )

    @staticmethod
    def _next_temp(
        current_temp: float, cooling_rate: float, increm_time_secs: float
    ) -> float:
        """This routine is to return the next temperature expected in a constant
        cooling rate based on the:

        Args:
            current_temp: initial temperature.
            cooling_rate: defined cooling rate (C / second).
            increm_time_secs: time increment interval in secs.

        Returns:
            float, the next temperature.
        """
        return float(current_temp - cooling_rate * increm_time_secs)

    def _transform_inc(
        self, tcurr: float, inc_time: float, phase_n_ratio: DynamicNdarray,
        phase_c_ratio: DynamicNdarray, phase_frac: DynamicNdarray,
        phase_vol: DynamicNdarray, cnt: int, integral_mat: np.ndarray
    ) -> None:

        # Stop counters
        # Start by setting them to Go
        stop_f, stop_p, stop_b = False, False, False
        # NOTE: This is passed by reference in Dr. Bendeich's code. Find out why
        stop_f_end, stop_p_end, stop_b_end = False, False, False

        # We need to maintain austenite at 100%
        if tcurr > self.ae3:
            phase_frac[cnt, 0] = phase_frac[cnt - 1, 0]

        # ================================================================== #
        # The below `numpy.ndarray` have the following columns:
        # 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite

        # Make current Austenite % same as last increment... and then adjust
        # below. Freeze all other phases at current levels at this point in the
        # cooling path.
        phase_frac[cnt, 0] = phase_frac[cnt - 1, 0]

        phase_frac[cnt, 1] = phase_frac[cnt - 1, 1]
        phase_frac[cnt, 2] = phase_frac[cnt - 1, 2]
        phase_frac[cnt, 3] = phase_frac[cnt - 1, 3]
        phase_frac[cnt, 4] = phase_frac[cnt - 1, 4]

        phase_n_ratio[cnt, 1] = phase_n_ratio[cnt - 1, 1]
        phase_n_ratio[cnt, 2] = phase_n_ratio[cnt - 1, 2]
        phase_n_ratio[cnt, 3] = phase_n_ratio[cnt - 1, 3]
        phase_n_ratio[cnt, 4] = phase_n_ratio[cnt - 1, 4]

        phase_c_ratio[cnt, 1] = phase_c_ratio[cnt - 1, 1]
        phase_c_ratio[cnt, 2] = phase_c_ratio[cnt - 1, 2]
        phase_c_ratio[cnt, 3] = phase_c_ratio[cnt - 1, 3]
        phase_c_ratio[cnt, 4] = phase_c_ratio[cnt - 1, 4]

        # make current volume % is the same as last increment... and then
        # adjust below
        # Freeze all other phases at current levels at this point in the
        # cooling path
        phase_vol[cnt, 0] = phase_vol[cnt - 1, 0]
        phase_vol[cnt, 1] = phase_vol[cnt - 1, 1]
        phase_vol[cnt, 2] = phase_vol[cnt - 1, 2]
        phase_vol[cnt, 3] = phase_vol[cnt - 1, 3]
        phase_vol[cnt, 4] = phase_vol[cnt - 1, 4]
        # ================================================================== #
        # Definitions of "integral2[,]"
        #
        # Kirkaldy:
        # [0,0], [0,1], [0,2]: spots for starting precipitation of F, P, and B
        # respectively.
        # [1,0], [1,1], [1,2]: spots for finishing precipitation of  F, P, and B
        # respectively.
        #
        # Li98:
        # [2,0], [2,1], [2,2]: spots for starting precipitation of F, P, and B
        # respectively
        # [3,0], [3,1], [3,2]: spots for finishing precipitation of F, P, and B
        # respectively
        if tcurr <= self.ms:
            # Convert remaining austenite to Martensite (this is done
            # progressively with anisothermal undercooling, time is not
            # relevant, only delta T under Ms)

            # Look for Martensite growth (there may be no Austenite left to
            # form Martensite)

            # Initial Austenite volume at the beginning of this phase.

            # Beginning Austenite-Martensite vol from now to completed
            # Martensite transformation (initial total volume Aust - total vol
            # Ferrite, Bainite, Pearlite). Martensite not included on purpose.
            aust_vol_m = phase_vol[1, 0] - (
                phase_vol[cnt, 1] + phase_vol[cnt, 2] + phase_vol[cnt, 3]
            )

            # Introduce new progressive temperature dependent Martensite
            # transformation (June 2019) using Koistinen and Marbuger eqn.
            phase_frac[cnt, 4] = (
                1 - exp(-self.ms_rate_param * (self.ms - tcurr))
            ) * aust_vol_m / 100
            # Updates the fraction of remaining Austenite
            phase_frac[cnt, 0] = phase_frac[cnt, 0] - phase_frac[cnt, 4]

            # Get the existing total Martensite volume from the previous
            # increment and add the new incremental volume increase.
            # Also deduct this incremental volume from the remaining Austenite
            # volume (yes and no ... be careful)
            # PhaseFrac(count,4) is the fraction of the total volume (100%)
            # that is Martensite
            phase_vol[cnt, 4] = 100 * phase_frac[cnt, 4]
            # Update the  actual vol Austenite remaining after this increment
            phase_vol[cnt, 0] = aust_vol_m - (
                aust_vol_m * (phase_frac[cnt, 4] / (aust_vol_m / 100))
            )

            stop_f, stop_p, stop_b = True, True, True
            stop_f_end, stop_p_end, stop_b_end = True, True, True

        # if above the martensite transformation temperature then we are
        # looking for any phase that might occur
        if self.ms < tcurr < self.ae3:
            # Find the total time to nucleation at the current temperature
            # and divide the current increment time by this to find the
            # fraction consumed in the current step
            # Then add this to the previous total for the relevant phases
            # When the total is 1.0 nucleation has occurred

            # 0=Austenite, 1=Ferrite, 2=Pearlite, 3=Bainite, 4=Martensite,
            # 5=(spare)

            # =============== # LOOK FOR BAINITE (3) START # =============== #
            if (
                tcurr < self.bs and phase_n_ratio[cnt - 1, 3] < 1.0 and stop_b
            ):
                # Transformation time for bainite start
                torr_b = self._torr_calc2(
                    phase=Phase.B, tcurr=tcurr, integral_mat=integral_mat, i=1
                )

                # Add up the cumulative fraction of Austenite converted towards
                # the nucleation point
                phase_n_ratio[cnt, 3] = (
                    phase_n_ratio[cnt - 1, 3] + (inc_time / torr_b)
                )
            # =============== # LOOK FOR BAINITE (3) FINISH # =============== #
            if (
                tcurr < self.bs and phase_c_ratio[cnt - 1, 3] < 1.0
                and not stop_b_end
            ):
                # Transformation time for bainite finish
                torr_b_end = self._torr_calc2(
                    phase=Phase.B, tcurr=tcurr, integral_mat=integral_mat, i=2
                )
                # Add up the cumulative fraction of austenite converted toward
                # the nucleation point
                phase_c_ratio[cnt, 3] = (
                    phase_c_ratio[cnt - 1, 3] + (inc_time / torr_b_end)
                )
            # =============== # LOOK FOR BAINITE (3) GROWTH # =============== #
            # Nucleation started but not yet finished
            if (
                phase_n_ratio[cnt - 1, 3] > 1.0 > phase_c_ratio[cnt - 1, 3]
                and not stop_b_end
            ):
                # Time interval between initiation and completion at current
                # temperature

                # If Bainite is growing then neither Ferrite or Pearlite growth
                # are possible anymore (not entirely true as small Ferrite
                # overlap can exist)
                # Freeze current levels and stop further growth
                # Ferrite
                phase_frac[cnt, 1] = phase_frac[cnt - 1, 1]
                # Pearlite
                phase_frac[cnt, 2] = phase_frac[cnt - 1, 2]

                stop_f, stop_p = True, True
                stop_f_end, stop_p_end = True, True

                # Transformation time for bainite start and finish
                torr_b = self._torr_calc2(
                    phase=Phase.B, tcurr=tcurr, integral_mat=integral_mat, i=1
                )
                torr_b_end = self._torr_calc2(
                    phase=Phase.B, tcurr=tcurr, integral_mat=integral_mat, i=2
                )
                delta_t = torr_b_end - torr_b
                phase_frac[cnt, 3] = (
                    phase_frac[cnt - 1, 3] + (inc_time / delta_t)
                )
                # Initial Austenite volume at the beginning of this phase
                # Beginning Austenite-Ferrite vol from now completed Ferrite
                # transformation (initial total volume Aust - total vol Ferrite)

                aust_vol_b = (
                    phase_vol[1, 0] - phase_vol[cnt, 1] - phase_vol[cnt, 2]
                )
                # Note Ferrite & Pearlite vol won't (or shouldn't) change
                # from here on

                # Get the existing total Pearlite volume from the previous
                # increment and add the new incremental volume increase of
                # Pearlite.
                # Also deduct this incremental volume from the remaining
                # Austenite volume
                # Convert the fraction of remaining Austenite to a volume of
                # Pearlite and add to the existing Volume of Pearlite
                phase_vol[cnt, 3] = (
                    phase_vol[cnt - 1, 3] +
                    ((inc_time / delta_t) * aust_vol_b)
                )
                # Update the actual vol Austenite remaining after this increment
                phase_vol[cnt, 0] = (
                    phase_vol[cnt, 0] - ((inc_time / delta_t) * aust_vol_b)
                )

                # Slight overshoot so trim from volume so it cant be negative
                if phase_vol[cnt, 0] < 0:
                    # Deduct the overshoot from the current phase volume to
                    # make it balance
                    phase_vol[cnt, 3] = phase_vol[cnt, 3] + phase_vol[cnt, 0]
                    # No Austenite left
                    phase_vol[cnt, 0] = 0

                # Stop obvious overshoot on last pass through here by capping
                # at 100% of current Austenite volume
                overshoot_ratio_b = 1
                if phase_vol[cnt, 3] > aust_vol_b:
                    overshoot_ratio_b = aust_vol_b / phase_vol[cnt, 3]
                    phase_vol[cnt, 3] = aust_vol_b

                # If Bainite is growing then this must be deducted from
                # Austenite
                phase_frac[cnt, 0] = (
                    phase_frac[cnt - 1, 0] -
                    ((inc_time / delta_t) * overshoot_ratio_b)
                )

            # =============== # LOOK FOR PEARLITE (2) START # =============== #
            if (
                tcurr < self.ae1 and phase_n_ratio[cnt - 1, 2] < 1.0
                and not stop_p
            ):
                # Transformation time for pearlite start
                torr_p = self._torr_calc2(
                    phase=Phase.P, tcurr=tcurr, integral_mat=integral_mat, i=1
                )
                # Add up the cumulative fraction of Pearlite converted
                # toward the nucleation point
                phase_n_ratio[cnt, 2] = (
                    phase_n_ratio[cnt - 1, 2] + (inc_time / torr_p)
                )
            # =============== # LOOK FOR PEARLITE (2) FINISH # =============== #
            if (
                tcurr < self.ae1 and phase_c_ratio[cnt - 1, 2] < 1.0
                and not stop_p_end
            ):
                # Transformation time for pearlite finish
                torr_p_end = self._torr_calc2(
                    phase=Phase.P, tcurr=tcurr, integral_mat=integral_mat, i=2
                )
                # Add up the cumulative fraction of Pearlite converted toward
                # the nucleation point
                phase_c_ratio[cnt, 2] = (
                    phase_c_ratio[cnt - 1, 2] + (inc_time / torr_p_end)
                )
            # =============== # LOOK FOR PEARLITE (2) GROWTH # =============== #
            if (
                tcurr < self.ae1
                and phase_n_ratio[cnt - 1, 2] > 1.0 > phase_c_ratio[cnt - 1, 2]
                and not stop_p_end
            ):
                # If Pearlite is growing then straight Ferrite is not
                # possible anymore
                # Freeze current levels and stop further growth
                # Ferrite
                phase_frac[cnt, 1] = phase_frac[cnt - 1, 1]
                stop_f, stop_f_end = True, True

                torr_p = self._torr_calc2(
                    phase=Phase.P, tcurr=tcurr, integral_mat=integral_mat, i=1
                )
                torr_p_end = self._torr_calc2(
                    phase=Phase.P, tcurr=tcurr, integral_mat=integral_mat, i=2
                )
                delta_t = torr_p_end - torr_p
                phase_frac[cnt, 2] = (
                    phase_frac[cnt - 1, 2] + (inc_time / delta_t) +
                    (1 - self.xfe)
                )

                # Initial Austenite volume at the beginning of this phase
                # Beginning Austenite-Ferrite vol from now completed Ferrite
                # transformation (initial total volume Aust - total vol Ferrite)
                aust_vol_p = phase_vol[1, 0] - phase_vol[cnt, 1]
                # Note Ferrite vol wont (or shouldn't) change from here on

                # Get the existing total Pearlite volume from the previous
                # increment and add the new incremental volume increase of
                # Pearlite.

                # Also deduct this incremental volume from the remaining
                # Austenite volume
                phase_vol[cnt, 2] = (
                    phase_vol[cnt - 1, 2] +
                    ((inc_time / delta_t) * aust_vol_p)
                )
                # Update the actual vol Austenite remaining after this increm
                phase_vol[cnt, 0] = (
                    phase_vol[cnt, 0] - ((inc_time / delta_t) * aust_vol_p)
                )

                # Slight overshoot for complete Austenite exhaustion so trim
                # from volume so it can't be negative
                if phase_vol[cnt, 0] < 0:
                    phase_vol[cnt, 2] = phase_vol[cnt, 2] + phase_vol[cnt, 0]
                    # No Austenite left
                    phase_vol[cnt, 0] = 0

                # Stop obvious overshoot on last pass through here by capping
                # at 100% of current Austenite volume
                overshoot_ratio_p = 1
                if phase_vol[cnt, 2] > aust_vol_p:
                    overshoot_ratio_p = aust_vol_p / phase_vol[cnt, 2]
                    phase_vol[cnt, 2] = aust_vol_p

                # If Pearlite is growing then this must be deducted from
                # Austenite
                phase_frac[cnt, 0] = (
                    phase_frac[cnt - 1, 0] - (
                        (inc_time / delta_t) *
                        (1 - self.xfe) * overshoot_ratio_p
                    )
                )

            # =============== # LOOK FOR FERRITE (1) START # =============== #
            # Headed toward nucleation but not there yet
            if (
                tcurr < self.ae3 and phase_n_ratio[cnt - 1, 1] < 1.0
                and not stop_f
            ):
                # Transformation time for ferrite start
                torr_f = self._torr_calc2(
                    phase=Phase.F, tcurr=tcurr, integral_mat=integral_mat, i=1
                )
                phase_n_ratio[cnt, 1] = (
                    phase_n_ratio[cnt - 1, 1] + (inc_time / torr_f)
                )

            # =============== # LOOK FOR FERRITE (1) FINISH # =============== #
            # Headed toward full precipitation completion but not there yet
            # but anywhere up to this point (pre-nucleation or nucleated and
            # growing)
            if (
                tcurr < self.ae3 and phase_c_ratio[cnt - 1, 1] < 1.0
                and not stop_f_end
            ):
                # Transformation time for ferrite finish
                torr_f_end = self._torr_calc2(
                    phase=Phase.F, tcurr=tcurr, integral_mat=integral_mat, i=2
                )
                # Add up the cumulative fraction of austenite converted toward
                # 100% (note this is % of equilibrium phase fraction, Xfe)
                phase_n_ratio[cnt, 1] = (
                    phase_n_ratio[cnt - 1, 1] + (inc_time / torr_f_end)
                )

            # =============== # LOOK FOR FERRITE (1) GROWTH # =============== #
            # Nucleation started but not yet finished
            if (
                tcurr < self.ae3
                and phase_n_ratio[cnt - 1, 1] > 1.0 > phase_c_ratio[cnt - 1, 1]
                and not stop_f_end
            ):
                torr_f = self._torr_calc2(
                    phase=Phase.F, tcurr=tcurr, integral_mat=integral_mat, i=1
                )
                torr_f_end = self._torr_calc2(
                    phase=Phase.F, tcurr=tcurr, integral_mat=integral_mat, i=2
                )
                # Find the total time expected between nucleation and
                # completion <<<< AT THE CURRENT TEMPERATURE >>>
                # This will change in each increment
                delta_t = torr_f_end - torr_f
                # Get the TOTAL phase fraction nucleated by the end of this
                # increment. (prior total + the current increment)
                phase_frac[cnt, 1] = (
                    phase_frac[cnt - 1, 1] + (inc_time / delta_t) * self.xfe
                )

                # This bit above uses a linear interpolation of nucleation
                # which is not accurate as it is a sigmoidal nucleation
                # distribution consider updating in future

                # Initial Austenite volume at the beginning of this phase
                # Beginning Austenite-Ferrite vol from now completed Ferrite
                # transformation
                # Initial total volume Austenite at start of whole process
                aust_vol_f = phase_vol[1, 0]

                # Get the existing total Ferrite volume from the previous
                # increment and add the new incremental volume increase of
                # Ferrite.
                # Also deduct the incremental volume from the remaining Aust.

                # Note that Ferrite can only exist between 0 and Xfe, the
                # equilibrium phase fraction. at 100% ferrite nucleation its
                # % volume cannot exceed Xfe * total volume (or initial
                # austenite volume)
                phase_vol[cnt, 1] = (
                    phase_vol[cnt - 1, 1] +
                    ((inc_time / delta_t) * phase_vol[1, 0] * self.xfe)
                )
                # Convert the fraction of Austenite available for conversion
                # to ferrite (Xfe) to a volume of Pearlite and add to the
                # existing Volume of Pearlite
                phase_vol[cnt, 0] = phase_vol[1, 0] - phase_vol[cnt, 1]

                # Slight overshoot for complete Austenite exhaustion so trim
                # from volume so it can't be negative
                if phase_vol[cnt, 0] < 0:
                    # Deduct the overshoot from the current phase volume to
                    # make it balance
                    phase_vol[cnt, 1] = phase_vol[cnt, 1] - phase_vol[cnt, 0]
                    # No Austenite left
                    phase_vol[cnt, 0] = 0

                # Stop obvious overshoot (on equilibrium fraction limit) on
                # last pass through here by capping at 100%
                overshoot_ratio_f = 1
                if phase_vol[cnt, 1] > aust_vol_f * self.xfe:
                    overshoot_ratio_f = (
                        (aust_vol_f * self.xfe) / phase_vol[cnt, 1]
                    )
                    phase_vol[cnt, 1] = aust_vol_f * self.xfe

                # If Ferrite is growing then this must be deducted from current
                # Austenite volume or fraction
                phase_frac[cnt, 0] = (
                    phase_frac[cnt - 1, 0] -
                    ((inc_time / delta_t) * self.xfe * overshoot_ratio_f)
                )
        # Work out the ratio to nucleation for each phase

        # Once nucleation identified work out % conversion to the new phase
        # and reduce available Austenite for the next iteration
        # If Ferrite nucleation occurs 1st then follow until either:
        #  - the equilibrium Volume fraction of ferrite is achieved (at the
        #    current temperature ... this can vary)
        #  - Pearlite nucleation starts (discontinue Ferrite growth) and
        #    follow Pearlite growth (maximum should be remaining
        #    fraction = equilibrium fraction of Pearlite)
        #  - Bainite nucleation occurs (discontinue either Ferrite or Pearlite
        #    growth if either has started) and grow until either all remaining
        #    volume consumed OR MS reached

        # Record the fraction of each Phase at every time interval
        # ==================== # END OF TRANSFORM_INC # ==================== #
