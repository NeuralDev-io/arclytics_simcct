# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# simconfiguration.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'Arvy Salazar <@Xaraox>']
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.24'
__package__ = 'simulation'
"""simconfiguration.py: 

{Description}
"""

import os
import json
from pathlib import Path

import numpy as np
from prettytable import PrettyTable

from simulation.utilities import Method, Alloy
from simulation.ae3_utilities import (
    ae3_single_carbon, convert_wt_2_mol, ae3_multi_carbon
)

BASE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
DEFAULT_CONFIGS = Path(BASE) / 'simulation' / 'sim_configs.json'


class SimConfiguration(object):
    """The SimConfiguration instance stores all the required arguments needed
    to simulate the Time-Temperature Transformation or the Cooling Curve
    Transformation. It also has methods to calculate some of these arguments
    automatically based on the Li '98 or Kirkaldy '83 equations as aggregated
    by Dr. Bendeich.
    """

    def __init__(self, configs: dict = None, compositions: list = None,
                 debug: bool = False):

        if debug:
            with open(DEFAULT_CONFIGS) as config_f:
                sim_configs = json.load(config_f, parse_float=np.float64)
            configs = sim_configs['configurations']
            compositions = sim_configs['compositions']

        if compositions is not None:
            self.comp = self.get_compositions(compositions)

        if configs is not None:
            self.method = (Method.Li98
                           if configs['method'] == 'Li98'
                           else Method.Kirkaldy83)

            self.alloy = Alloy.Parent
            if configs['alloy'] == 'mix':
                self.alloy = Alloy.Mix
            elif configs['alloy'] == 'weld':
                self.alloy = Alloy.Weld

            self.nuc_start = configs['nucleation_start'] / 100
            self.nuc_finish = configs['nucleation_finish'] / 100
            self.grain_type = configs['grain_size_type']
            self.grain_size = configs['grain_size']
            self.auto_xfe_calc = configs['auto_calculate_xfe']
            self.xfe = configs['xfe_value']
            self.cf = configs['cf_value']
            self.ceut = configs['ceut_value']
            self.auto_ms_bs_calc = configs['auto_calculate_ms_bs']
            self.ms_temp = configs['ms_temp']
            self.ms_undercool = configs['ms_undercool']
            self.bs_temp = configs['bs_temp']
            self.auto_austenite_calc = configs['auto_calculate_ae']
            self.ae1 = configs['ae1_temp']
            self.ae3 = configs['ae3_temp']
            self.temp_peak = configs['start_temperature']
            self.cct_cooling_rate = configs['cct_cooling_rate']

            self.ae_check = False
            if self.ae1 > 0 and self.ae3 > 0:
                self.ae_check = True

        if self.auto_ms_bs_calc:
            self.auto_ms_bs()
        if self.auto_austenite_calc:
            self.auto_ae1_ae3()
        if self.auto_xfe_calc:
            self.xfe_method2()

    @staticmethod
    def get_compositions(comp_list: list = None) -> np.ndarray:
        """
        We get the compositions from the list passed and extract the
        compositions as a list from parent, weld, and mix. We then store
        them as a Structured numpy.ndarray with ('name', 'symbol', 'weight')
        record types.
        Args:
            comp_list: a list of composition elements and weights.

        Returns:
            A structured numpy.ndarray with the weights and names.
        """
        comp = np.zeros(len(comp_list),
                        dtype=[
                            ('idx', np.int),
                            ('name', 'U20'),
                            ('symbol', 'U2'),
                            ('weight', np.float64)
                        ])
        # iterate over lists at once and store them in the np.ndarray
        for i, e in enumerate(comp_list):
            comp[i] = (i, e['name'], e['symbol'], e['value'])
        return comp

    def auto_ms_bs(self) -> None:
        """
        We simply store the class variables bs_temp and ms_temp by doing
        the calculations.
        """
        self.bs_temp = self.get_bs(self.method, self.comp)
        self.ms_temp = self.get_ms(self.method, self.comp)

    @staticmethod
    def get_bs(method: Method = None, comp: np.ndarray = None) -> float:
        """
        Do the calculation based on Li98 or Kirkaldy 83 method and return
        the MS temperature.
        """
        # TODO(andrew@neuraldev.io -- Sprint 6): Do some validation for these
        #  and return a tuple instead (float, error)
        # ensure we are getting the value and not the list by using index 0
        c = comp[comp['name'] == 'carbon']['weight'][0]
        mn = comp[comp['name'] == 'manganese']['weight'][0]
        ni = comp[comp['name'] == 'nickel']['weight'][0]
        cr = comp[comp['name'] == 'chromium']['weight'][0]
        mo = comp[comp['name'] == 'molybdenum']['weight'][0]

        if method == Method.Li98:
            # Eqn [24] in paper. Li modified from Kirkaldy.
            return (637.0 - (58 * c) - (35 * mn) -
                    (15 * ni) - (34 * cr) - (41 * mo))

        if method == Method.Kirkaldy83:
            # Eqn [30] in Kirkaldy defined 1983 paper
            return (656 - (58 * c) - (35 * mn) -
                    (15 * ni) - (34 * cr) - (41 * mo))

        return -1

    @staticmethod
    def get_ms(method: Method = None, comp: np.ndarray = None) -> float:
        """
        Do the calculation based on Li98 or Kirkaldy83 method and return the
        MS temperature.
        """
        # TODO(andrew@neuraldev.io -- Sprint 6): Do some validation for these
        #  and return a tuple instead (float, error)
        # ensure we are getting the value and not the list by using index 0
        c = comp[comp['name'] == 'carbon']['weight'][0]
        mn = comp[comp['name'] == 'manganese']['weight'][0]
        ni = comp[comp['name'] == 'nickel']['weight'][0]
        cr = comp[comp['name'] == 'chromium']['weight'][0]
        mo = comp[comp['name'] == 'molybdenum']['weight'][0]
        co = comp[comp['name'] == 'cobalt']['weight'][0]
        si = comp[comp['name'] == 'silicon']['weight'][0]

        if method == Method.Li98:
            # Eqn [25] in paper by Kung and Raymond
            return (539 - (423 * c) - (30.4 * mn) - (17.7 * ni) -
                    (12.1 * cr) - (7.5 * mo) + (10.0 * co) - (7.5 * si))

        if method == Method.Kirkaldy83:
            # Eqn [31] in Kirkaldy 1983 paper
            return (561 - (474 * c) - (33.0 * mn) -
                    (17.0 * ni) - (17.0 * cr) - (21.0 * mo))

        return -1

    def auto_ae1_ae3(self) -> None:
        """Calculate the austenite values based on composition automatically."""
        # validate the Austenite values have been generated and it will not
        # crash the application
        self.ae_check = True
        self.ae1, self.ae3 = self.calc_ae1_ae3()

    def calc_ae1_ae3(self) -> (np.float, np.float):
        c = self.comp[self.comp['name'] == 'carbon']['weight'][0]
        ni = self.comp[self.comp['name'] == 'nickel']['weight'][0]
        si = self.comp[self.comp['name'] == 'silicon']['weight'][0]
        wx = self.comp[self.comp['name'] == 'tungsten']['weight'][0]
        mn = self.comp[self.comp['name'] == 'manganese']['weight'][0]
        cr = self.comp[self.comp['name'] == 'chromium']['weight'][0]
        asx = self.comp[self.comp['name'] == 'arsenic']['weight'][0]
        mo = self.comp[self.comp['name'] == 'molybdenum']['weight'][0]
        # Do the calculations
        # 1. Equations of Andrews (1965)
        ae1 = (
            723.0 - (16.9 * ni) + (29.1 * si) + (6.38 * wx) - (10.7 * mn) +
            (16.9 * cr) + (290 * asx)
        ) / 3.0

        # 2. Equations of Eldis (in Barralis, 1982): 1/3 due to averaging
        ae1 = ae1 + (
            712.0 - (17.8 * mn) - (19.1 * ni) + (20.1 * si) + (11.9 * cr) +
            (9.8 * mo)
        ) / 3.

        # 3. Equations of Grange (1961): 1/3 due to averaging, convert from F
        # to C (-32*(5/9))
        ae1 = ae1 + (
            1333.0 - (25.0 * mn) + (40.0 * si) + (42.0 * cr) -
            (26.0 * ni) - 32.0
        ) * 5.0 / (3.0 * 9.0)

        # find the Ae3 temperature at the alloy Carbon content Using
        # Ortho-equilibrium method
        ae3 = ae3_single_carbon(self.comp.copy(), c)
        return ae1, ae3 - 273

    def xfe_method2(self) -> None:
        """Second method for estimating Xfe using parra-equilibrium methodology
        to predict  the Ae3 values with increasing carbon content. To find
        the intercept with Ae1 (from simplified method) to determine the
        eutectic carbon content wt%. With this value and a suitable estimate
        of the ferrite carbon content (~0.02 wt%). With these limits ant the
        current alloy composition the lever rule can be used to determine the
        equilibrium phase fraction

        Returns:

        """
        wt = self.comp.copy()

        # TODO: Not sure why we need this
        # Mole fractions: c to ALL elements; y to Fe only (y not used)
        c_vect, y_vect = convert_wt_2_mol(wt)

        # now let's get onto the main routine

        # store results of each iteration of Carbon

        results_mat = np.zeros((1000, 22), dtype=np.float64)
        # reserve the initial carbon wt% as the main routine is passing back
        # another value despite being set "ByVal"
        wt_c = wt['weight'][wt['name'] == 'carbon'][0]

        # Find Ae3 for array of Carbon contents form 0.00 to 0.96 wt%
        # UPDATE wt, Results to CALL Ae3MultiC(wt, Results)
        ae3_multi_carbon(wt, results_mat)

        # TODO: We may or may not implement the Ae3 plot but we can if we want
        #    to. -- WE ARE GOING TO DO PLOT
        # We can view the Ae3 plot with a call to the following
        # CALL Ae3Plot(results_mat, self.ae1, wt_c)

        # Find the Ae3-Ae1 intercept Carbon content (Eutectic composition
        if self.ae1 > 0:
            for i in range(1000):
                if results_mat[i, 1] <= self.ae1:
                    self.ceut = results_mat[i, 0]
                    break

        # Now calculate the important bit the Xfe equilibrium phase fraction
        # of Ferrite
        tie_length = self.ceut - self.cf
        lever1 = tie_length - wt_c
        self.xfe = lever1 / tie_length

    @staticmethod
    def _pretty_str_tables(comp: np.ndarray) -> PrettyTable:
        """Simply gives us a prettier table for compositions."""
        table = PrettyTable(comp.dtype.names)
        table.float_format['weight'] = '.3'
        for row in comp:
            table.add_row(row)
        # table.set_style(MSWORD_FRIENDLY)
        table.align['name'] = 'l'
        table.align['symbol'] = 'l'
        table.align['weight'] = 'r'

        return table

    def __str__(self):
        comp_ = self._pretty_str_tables(self.comp)

        return """
-------------------------------------------------
PHASE SIMULATION CONFIGURATIONS
-------------------------------------------------
{:30}{}
{:30}{}
Transformation Definitions:
  {:28}{:.4f} %
  {:28}{:.4f} %
Grain Size:
  {:28}{:8}
  {:28}{:6.4f}
Equilibrium Phase Fractions:
  {:28}{}
  {:28}{:.4f}
  {:28}{:.4f} (weight %)
  {:28}{:.4f} (weight %)
Transformation Temp. Limits:
  {:28}{}
  {:28}{:.4f}
  {:28}{:.4f}
  {:28}{:.4f}
Austenite Limits: 
  {:28}{}
  {:28}{:.4f}
  {:28}{:.4f}

Alloy Composition:
Parent: 
{}
-------------------------------------------------
        """.format(
            'Method:', self.method.name, 'Alloy:', self.alloy.name,
            'Nucleation Start:', self.nuc_start, 'Nucleation End:',
            self.nuc_finish, 'Type:', self.grain_type, 'Value: ',
            self.grain_size, 'Auto Calculate:', self.auto_xfe_calc, 'Xfe:',
            self.xfe, 'Cf:', self.cf, 'Ceut:', self.ceut, 'Auto Calculate:',
            self.auto_ms_bs_calc, 'MS Temperature:', self.ms_temp,
            'MS Undercool: ', self.ms_undercool, 'BS Temperature: ',
            self.bs_temp, 'Auto Calculate:', self.auto_austenite_calc, 'Ae1:',
            self.ae1, 'Ae3:', self.ae3, comp_
        )
