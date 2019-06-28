# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# simconfiguration.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.0.1'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.24'
__package__ = 'simulation'

"""simconfiguration.py: 

{Description}
"""

import json
import enum
from pathlib import Path
from typing import *

import numpy as np
from prettytable import PrettyTable, MSWORD_FRIENDLY

from logger.arc_logger import AppLogger
from simulation.ae3_utilities import ae3_single_carbon
from configs.settings import BASE_DIR, APP_CONFIGS

DEFAULT_CONFIGS = Path(BASE_DIR) / 'configs' / 'sim_configs.json'
DEBUG = APP_CONFIGS['general']['debug']
logger = AppLogger(__name__)


class Method(enum.Enum):
    Li98 = 1
    Kirkaldy83 = 2


class Alloy(enum.Enum):
    Parent = 1
    Weld = 2
    Mix = 3


class SimConfiguration(object):
    """
    The SimConfiguration instance stores all the required arguments needed to simulate the Time-Temperature Transformation
    or the Cooling Curve Transformation. It also has methods to calculate some of these arguments automatically based
    on the Li '98 or Kirkaldy '83 equations as aggregated by Dr. Bendeich.
    """

    def __init__(self, method=Method.Li98, alloy=Alloy.Parent, configs=None, debug=False, *args, **kwargs):
        self.method = method
        self.alloy = alloy

        config = {}
        if debug:
            config = self._get_default_test_configs()
        else:
            # TODO: Add the instance variables passed to instantiation
            self.ms_temp = None
            self.bs_temp = None

            self.ae1 = 0
            self.ae3 = 0

            if self.ae1 > 0 and self.ae3 > 0:
                self.ae_check = True

        self.comp_parent = None
        self.comp_weld = None
        self.comp_mix = None
        self.get_compositions(config)

        if self.auto_ms_bs_calc:
            self.auto_ms_bs()
        if self.auto_austenite_calc:
            self.auto_ae1_ae3()

        if self.ae_check:
            # TODO: make sure simulation checks this
            pass

    def _get_default_test_configs(self) -> dict:
        with open(DEFAULT_CONFIGS) as config_f:
            config = json.load(config_f, parse_float=np.float64)
            self.method = Method.Li98 if config['method']['li98'] else Method.Kirkaldy83

        self.nuc_start = config['transformation_definitions']['nucleation_start']
        self.nuc_finish = config['transformation_definitions']['nucleation_finish']
        self.grain_type = config['grain_size']['type']
        self.grain_size = config['grain_size']['value']
        self.auto_xfe_calc = config['equilibrium_phase_fractions']['auto_calculate']
        self.xfe = config['equilibrium_phase_fractions']['xfe_value']
        self.cf = config['equilibrium_phase_fractions']['cf_value']
        self.ceut = config['equilibrium_phase_fractions']['ceut_value']
        self.auto_ms_bs_calc = config['transformation_temp_limits']['auto_calculate']
        self.ms_temp = config['transformation_temp_limits']['ms_temp']
        self.ms_undercool = config['transformation_temp_limits']['ms_undercool']
        self.bs_temp = config['transformation_temp_limits']['bs_temp']
        self.auto_austenite_calc = config['austenite_limits']['auto_calculate']
        # TODO: Need to check if Ae available or can be calculated
        self.ae_check = False
        self.ae1 = config['austenite_limits']['ae1_value']
        self.ae3 = config['austenite_limits']['ae3_value']

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

        self.comp_parent = np.zeros(len(c_parent),
                                    dtype=[('idx', np.int), ('name', 'U20'), ('symbol', 'U2'), ('weight', np.float64)])
        self.comp_weld = np.zeros(len(c_weld),
                                  dtype=[('idx', np.int), ('name', 'U20'), ('symbol', 'U2'), ('weight', np.float64)])
        self.comp_mix = np.zeros(len(c_mix),
                                 dtype=[('idx', np.int), ('name', 'U20'), ('symbol', 'U2'), ('weight', np.float64)])

        # iterate over all 3 lists at once and store them in the np.ndarray
        for i, (e_p, e_w, e_m) in enumerate(zip(c_parent, c_weld, c_mix)):
            self.comp_parent[i] = (i, e_p['name'], e_p['symbol'], e_p['value'])
            self.comp_weld[i] = (i, e_w['name'], e_w['symbol'], e_w['value'])
            self.comp_mix[i] = (i, e_m['name'], e_m['symbol'], e_m['value'])

    def auto_ms_bs(self) -> None:
        """We simply store the class variables bs_temp and ms_temp by doing the calculations."""
        self.bs_temp = self.get_bs()
        self.ms_temp = self.get_ms()

    def get_bs(self) -> float:
        """Do the calculation based on Li98 or Kirkaldy 83 method and return the MS temperature."""
        # ensure we are getting the value and not the list by using index 0
        C = self.comp_parent[self.comp_parent['name'] == 'carbon']['weight'][0]
        Mn = self.comp_parent[self.comp_parent['name'] == 'manganese']['weight'][0]
        Ni = self.comp_parent[self.comp_parent['name'] == 'nickel']['weight'][0]
        Cr = self.comp_parent[self.comp_parent['name'] == 'chromium']['weight'][0]
        Mo = self.comp_parent[self.comp_parent['name'] == 'molybdenum']['weight'][0]

        if self.method == Method.Li98:
            # Eqn [24] in paper. Li modified from Kirkaldy.
            return 637.0 - (58 * C) - (35 * Mn) - (15 * Ni) - (34 * Cr) - (41 * Mo)

        if self.method == Method.Kirkaldy83:
            # Eqn [30] in Kirkaldy defined 1983 paper
            return 656 - (58 * C) - (35 * Mn) - (15 * Ni) - (34 * Cr) - (41 * Mo)
        return -1

    def get_ms(self) -> float:
        """Do the calculation based on Li98 or Kirkaldy83 method and return the MS temperature."""
        # ensure we are getting the value and not the list by using index 0
        C = self.comp_parent[self.comp_parent['name'] == 'carbon']['weight'][0]
        Mn = self.comp_parent[self.comp_parent['name'] == 'manganese']['weight'][0]
        Ni = self.comp_parent[self.comp_parent['name'] == 'nickel']['weight'][0]
        Cr = self.comp_parent[self.comp_parent['name'] == 'chromium']['weight'][0]
        Mo = self.comp_parent[self.comp_parent['name'] == 'molybdenum']['weight'][0]
        Co = self.comp_parent[self.comp_parent['name'] == 'cobalt']['weight'][0]
        Si = self.comp_parent[self.comp_parent['name'] == 'silicon']['weight'][0]

        if self.method == Method.Li98:
            # Eqn [25] in paper by Kung and Raymond
            return 539 - (423 * C) - (30.4 * Mn) - (17.7 * Ni) - (12.1 * Cr) - (7.5 * Mo) + (10.0 * Co) - (7.5 * Si)

        if self.method == Method.Kirkaldy83:
            # Eqn [31] in Kirkaldy 1983 paper
            return 561 - (474 * C) - (33.0 * Mn) - (17.0 * Ni) - (17.0 * Cr) - (21.0 * Mo)

        return -1

    def auto_ae1_ae3(self) -> None:
        # validate the Austenite values have been generated and it will not crash the application
        self.ae_check = True
        self.ae1, self.ae3 = self.calc_ae1_ae3()

    def calc_ae1_ae3(self) -> (np.float, np.float):
        c = self.comp_parent[self.comp_parent['name'] == 'carbon']['weight'][0]
        ni = self.comp_parent[self.comp_parent['name'] == 'nickel']['weight'][0]
        si = self.comp_parent[self.comp_parent['name'] == 'silicon']['weight'][0]
        wx = self.comp_parent[self.comp_parent['name'] == 'tungsten']['weight'][0]
        mn = self.comp_parent[self.comp_parent['name'] == 'manganese']['weight'][0]
        cr = self.comp_parent[self.comp_parent['name'] == 'chromium']['weight'][0]
        asx = self.comp_parent[self.comp_parent['name'] == 'arsenic']['weight'][0]
        mo = self.comp_parent[self.comp_parent['name'] == 'molybdenum']['weight'][0]
        vx = self.comp_parent[self.comp_parent['name'] == 'vanadium']['weight'][0]
        cu = self.comp_parent[self.comp_parent['name'] == 'copper']['weight'][0]
        px = self.comp_parent[self.comp_parent['name'] == 'phosphorous']['weight'][0]
        al = self.comp_parent[self.comp_parent['name'] == 'aluminium']['weight'][0]
        ti = self.comp_parent[self.comp_parent['name'] == 'titanium']['weight'][0]
        # Do the calculations
        # 1. Equations of Andrews (1965)
        ae1 = (723.0 - (16.9 * ni) + (29.1 * si) + (6.38 * wx) - (10.7 * mn) + (16.9 * cr) + (290 * asx)) / 3.0
        ae3 = (910.0 - (203 * np.sqrt(c)) + (44.7 * si) - (15.2 * ni) + (31.5 * mo) + (104.0 * vx) + (13.1 * wx) -
               (30 * mn) + (11.0 * cr) + (20.0 * cu) - (700.0 * px) - (400.0 * al) - (120.0 * asx) - (400.0 * ti)) / 3.0

        # 2. Equations of Eldis (in Barralis, 1982): 1/3 due to averaging
        ae1 = ae1 + (712.0 - (17.8 * mn) - (19.1 * ni) + (20.1 * si) + (11.9 * cr) + (9.8 * mo)) / 3.
        ae3 = ae3 + (871.0 - (254.4 * np.sqrt(c)) - (14.2 * ni) + (51.7 * si)) / 3.0

        # 3. Equations of Grange (1961): 1/3 due to averaging, convert from F to C
        # (-32*(5/9))
        ae1 = ae1 + (1333.0 - (25.0 * mn) + (40.0 * si) + (42.0 * cr) - (26.0 * ni) - 32.0) * 5.0 / (3.0 * 9.0)
        ae3 = ae3 + (1570.0 - (323.0 * c) - (25.0 * mn) + (80.0 * si) - (3.0 * cr) - (32.0 * ni) -
                     32.0) * 5.0 / (3.0 * 9.0)

        # NOTE: Check the results of ae1 and ae3 at this point

        # find the Ae3 temperature at the alloy Carbon content Using Ortho-equilibrium method
        # ae3 = ae3_single_carbon(self.comp_parent.copy(), c)

        return ae1, ae3 - 273

    @staticmethod
    def _pretty_str_tables(comp: np.ndarray) -> PrettyTable:
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
{:9}{}
{:9}{}
Transformation Definitions:
  {:19}{:.4f} %
  {:19}{:.4f} %
Grain Size:
  {:8}{:8}
  {:8}{:6.4f}
Equilibrium Phase Fractions:
  {:8}{:.4f}
  {:8}{:.4f} (weight %)
  {:8}{:.4f} (weight %)
Transformation Temperature Limits:
  {:17}{:.4f}
  {:17}{:.4f}
  {:17}{:.4f}
Austenite Limits: 
  {:6}{:.4f}
  {:6}{:.4f}
Alloy Composition:
Parent: 
{}
Weld:
{}
Mix:
{}
        """.format(
            'Method:', self.method.name, 'Alloy:', self.alloy.name,
            'Nucleation Start:', self.nuc_start, 'Nucleation End:', self.nuc_finish,
            'Type:', self.grain_type, 'Value: ', self.grain_size,
            'Xfe:', self.xfe, 'Cf:', self.cf, 'Ceut:', self.ceut,
            'MS Temperature:', self.ms_temp, 'MS Undercool: ', self.ms_undercool,
            'BS Temperature: ', self.bs_temp,
            'Ae1:', self.ae1, 'Ae3:', self.ae3,
            parent_t, weld_t, mix_t
        )
