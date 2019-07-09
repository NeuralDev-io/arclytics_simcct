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
# from logger.arc_logger import AppLogger
from simulation.ae3_utilities import (
    ae3_single_carbon, convert_wt_2_mol, ae3_multi_carbon
)

BASE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
DEFAULT_CONFIGS = Path(BASE) / 'simulation' / 'sim_configs.json'
# DEBUG = APP_CONFIGS['general']['debug']
# logger = AppLogger(__name__)


class SimConfiguration(object):
    """The SimConfiguration instance stores all the required arguments needed
    to simulate the Time-Temperature Transformation or the Cooling Curve
    Transformation. It also has methods to calculate some of these arguments
    automatically based on the Li '98 or Kirkaldy '83 equations as aggregated
    by Dr. Bendeich.
    """

    def __init__(
        self,
        method=Method.Li98,
        alloy=Alloy.Parent,
        configs=None,
        debug=False,
    ):
        self.method = method
        self.alloy = alloy

        self.configs = configs
        if debug:
            self.configs = self._get_default_test_configs()

        if configs is not None:
            self.nuc_start = self.configs['transformation_definitions'
                                          ]['nucleation_start'] / 100
            self.nuc_finish = self.configs['transformation_definitions'
                                           ]['nucleation_finish'] / 100
            self.grain_type = self.configs['grain_size']['type']
            self.grain_size = self.configs['grain_size']['value']
            self.auto_xfe_calc = self.configs['equilibrium_phase_fractions'
                                              ]['auto_calculate']
            self.xfe = self.configs['equilibrium_phase_fractions']['xfe_value']
            self.cf = self.configs['equilibrium_phase_fractions']['cf_value']
            self.ceut = self.configs['equilibrium_phase_fractions'
                                     ]['ceut_value']
            self.auto_ms_bs_calc = self.configs['transformation_temp_limits'
                                                ]['auto_calculate']
            self.ms_temp = self.configs['transformation_temp_limits']['ms_temp'
                                                                      ]
            self.ms_undercool = self.configs['transformation_temp_limits'
                                             ]['ms_undercool']
            self.bs_temp = self.configs['transformation_temp_limits']['bs_temp'
                                                                      ]
            self.auto_austenite_calc = self.configs['austenite_limits'
                                                    ]['auto_calculate']
            self.ae1 = self.configs['austenite_limits']['ae1_value']
            self.ae3 = self.configs['austenite_limits']['ae3_value']
            self.temp_peak = self.configs['cooling_profile'
                                          ]['start_temperature']
            self.cct_cooling_rate = self.configs['cooling_profile'
                                                 ]['cct_cooling_rate']

            self.ae_check = False
            if self.ae1 > 0 and self.ae3 > 0:
                self.ae_check = True

        self.comp_parent = None
        self.comp_weld = None
        self.comp_mix = None
        self.get_compositions(self.configs)

        if self.auto_ms_bs_calc:
            self.auto_ms_bs()
        if self.auto_austenite_calc:
            self.auto_ae1_ae3()
        if self.auto_xfe_calc:
            self.xfe_method2()

    def _get_default_test_configs(self) -> dict:
        with open(DEFAULT_CONFIGS) as config_f:
            config = json.load(config_f, parse_float=np.float64)
            self.method = Method.Li98 if config['method'][
                'li98'] else Method.Kirkaldy83

        self.nuc_start = config['transformation_definitions'
                                ]['nucleation_start'] / 100
        self.nuc_finish = config['transformation_definitions'
                                 ]['nucleation_finish'] / 100
        self.grain_type = config['grain_size']['type']
        self.grain_size = config['grain_size']['value']
        self.auto_xfe_calc = config['equilibrium_phase_fractions'
                                    ]['auto_calculate']
        self.xfe = config['equilibrium_phase_fractions']['xfe_value']
        self.cf = config['equilibrium_phase_fractions']['cf_value']
        self.ceut = config['equilibrium_phase_fractions']['ceut_value']
        self.auto_ms_bs_calc = config['transformation_temp_limits'
                                      ]['auto_calculate']
        self.ms_temp = config['transformation_temp_limits']['ms_temp']
        self.ms_undercool = config['transformation_temp_limits']['ms_undercool'
                                                                 ]
        self.bs_temp = config['transformation_temp_limits']['bs_temp']
        self.auto_austenite_calc = config['austenite_limits']['auto_calculate']
        # TODO: Need to check if Ae available or can be calculated
        self.ae_check = False
        self.ae1 = config['austenite_limits']['ae1_value']
        self.ae3 = config['austenite_limits']['ae3_value']
        self.temp_peak = config['cooling_profile']['start_temperature']
        self.cct_cooling_rate = config['cooling_profile']['cct_cooling_rate']

        return config

    def get_compositions(self, config: dict) -> None:
        """
        We get the compositions from the JSON passed and extract the compositions as a list from
        parent, weld, and mix. We then store them as a Structured numpy.ndarray with ('name', 'symbol', 'weight')
        record types.
        Args:
            config: the JSON config dictionary that has already been read.

        Returns:
        None
        """
        c_parent = config['composition']['parent']
        c_weld = config['composition']['weld']
        c_mix = config['composition']['mix']

        self.comp_parent = np.zeros(
            len(c_parent),
            dtype=[
                ('idx', np.int), ('name', 'U20'), ('symbol', 'U2'),
                ('weight', np.float64)
            ]
        )
        self.comp_weld = np.zeros(
            len(c_weld),
            dtype=[
                ('idx', np.int), ('name', 'U20'), ('symbol', 'U2'),
                ('weight', np.float64)
            ]
        )
        self.comp_mix = np.zeros(
            len(c_mix),
            dtype=[
                ('idx', np.int), ('name', 'U20'), ('symbol', 'U2'),
                ('weight', np.float64)
            ]
        )

        # iterate over all 3 lists at once and store them in the np.ndarray
        for i, (e_p, e_w, e_m) in enumerate(zip(c_parent, c_weld, c_mix)):
            self.comp_parent[i] = (i, e_p['name'], e_p['symbol'], e_p['value'])
            self.comp_weld[i] = (i, e_w['name'], e_w['symbol'], e_w['value'])
            self.comp_mix[i] = (i, e_m['name'], e_m['symbol'], e_m['value'])

    def auto_ms_bs(self) -> None:
        """
        We simply store the class variables bs_temp and ms_temp by doing
        the calculations.
        """
        self.bs_temp = self.get_bs()
        self.ms_temp = self.get_ms()

    def get_bs(self) -> float:
        """
        Do the calculation based on Li98 or Kirkaldy 83 method and return
        the MS temperature.
        """

        # ensure we are getting the value and not the list by using index 0
        c = self.comp_parent[self.comp_parent['name'] == 'carbon']['weight'][0]
        mn = self.comp_parent[self.comp_parent['name'] == 'manganese'
                              ]['weight'][0]
        ni = self.comp_parent[self.comp_parent['name'] == 'nickel'
                              ]['weight'][0]
        cr = self.comp_parent[self.comp_parent['name'] == 'chromium'
                              ]['weight'][0]
        mo = self.comp_parent[self.comp_parent['name'] == 'molybdenum'
                              ]['weight'][0]

        if self.method == Method.Li98:
            # Eqn [24] in paper. Li modified from Kirkaldy.
            return 637.0 - (58 * c) - (35 * mn) - (15 * ni) - (34 *
                                                               cr) - (41 * mo)

        if self.method == Method.Kirkaldy83:
            # Eqn [30] in Kirkaldy defined 1983 paper
            return 656 - (58 * c) - (35 * mn) - (15 * ni) - (34 *
                                                             cr) - (41 * mo)
        return -1

    def get_ms(self) -> float:
        """
        Do the calculation based on Li98 or Kirkaldy83 method and return the
        MS temperature.
        """
        # ensure we are getting the value and not the list by using index 0
        c = self.comp_parent[self.comp_parent['name'] == 'carbon']['weight'][0]
        mn = self.comp_parent[self.comp_parent['name'] == 'manganese'
                              ]['weight'][0]
        ni = self.comp_parent[self.comp_parent['name'] == 'nickel'
                              ]['weight'][0]
        cr = self.comp_parent[self.comp_parent['name'] == 'chromium'
                              ]['weight'][0]
        mo = self.comp_parent[self.comp_parent['name'] == 'molybdenum'
                              ]['weight'][0]
        co = self.comp_parent[self.comp_parent['name'] == 'cobalt'
                              ]['weight'][0]
        si = self.comp_parent[self.comp_parent['name'] == 'silicon'
                              ]['weight'][0]

        if self.method == Method.Li98:
            # Eqn [25] in paper by Kung and Raymond
            return 539 - (423 * c) - (30.4 * mn) - (17.7 * ni) - (
                12.1 * cr
            ) - (7.5 * mo) + (10.0 * co) - (7.5 * si)

        if self.method == Method.Kirkaldy83:
            # Eqn [31] in Kirkaldy 1983 paper
            return 561 - (474 * c) - (33.0 * mn) - (17.0 *
                                                    ni) - (17.0 *
                                                           cr) - (21.0 * mo)

        return -1

    def auto_ae1_ae3(self) -> None:
        """Calculate the austenite values based on composition automatically."""
        # validate the Austenite values have been generated and it will not
        # crash the application
        self.ae_check = True
        self.ae1, self.ae3 = self.calc_ae1_ae3()

    def calc_ae1_ae3(self) -> (np.float, np.float):
        c = self.comp_parent[self.comp_parent['name'] == 'carbon']['weight'][0]
        ni = self.comp_parent[self.comp_parent['name'] == 'nickel'
                              ]['weight'][0]
        si = self.comp_parent[self.comp_parent['name'] == 'silicon'
                              ]['weight'][0]
        wx = self.comp_parent[self.comp_parent['name'] == 'tungsten'
                              ]['weight'][0]
        mn = self.comp_parent[self.comp_parent['name'] == 'manganese'
                              ]['weight'][0]
        cr = self.comp_parent[self.comp_parent['name'] == 'chromium'
                              ]['weight'][0]
        asx = self.comp_parent[self.comp_parent['name'] == 'arsenic'
                               ]['weight'][0]
        mo = self.comp_parent[self.comp_parent['name'] == 'molybdenum'
                              ]['weight'][0]
        vx = self.comp_parent[self.comp_parent['name'] == 'vanadium'
                              ]['weight'][0]
        cu = self.comp_parent[self.comp_parent['name'] == 'copper'
                              ]['weight'][0]
        px = self.comp_parent[self.comp_parent['name'] == 'phosphorous'
                              ]['weight'][0]
        al = self.comp_parent[self.comp_parent['name'] == 'aluminium'
                              ]['weight'][0]
        ti = self.comp_parent[self.comp_parent['name'] == 'titanium'
                              ]['weight'][0]
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
        ae3 = ae3_single_carbon(self.comp_parent.copy(), c)
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
        wt = self.comp_parent.copy()

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

        # Find the Ae3 temperature at the alloy Carbon content
        # TODO: Not sure why we need to set ae3 here.
        ae3 = ae3_single_carbon(wt, wt_c)

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
        parent_t = self._pretty_str_tables(self.comp_parent)
        weld_t = self._pretty_str_tables(self.comp_weld)
        mix_t = self._pretty_str_tables(self.comp_mix)

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
            self.ae1, 'Ae3:', self.ae3, parent_t, weld_t, mix_t
        )
