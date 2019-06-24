# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# simulation.py
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

"""simulation.py: 

{Description}
"""

import os
import json
import enum
from pathlib import Path
from typing import *

import numpy as np
from prettytable import PrettyTable

from logger.arc_logger import AppLogger

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
DEFAULT_CONFIGS = Path(BASE_DIR) / 'configs' / 'sim_configs.json'
logger = AppLogger(__name__)


class Method(enum.Enum):
    Li98 = 1
    Kirkaldy83 = 2


class Alloy(enum.Enum):
    Parent = 1
    Weld = 2
    Mix = 3


class Simulation(object):
    """
    The Simulation instance stores all the required arguments needed to simulate the Time-Temperature Transformation
    or the Cooling Curve Transformation. It also has methods to calculate some of these arguments automatically based
    on the Li '98 or Kirkaldy '83 equations as aggregated by Dr. Bendeich.
    """
    def __init__(self, method=Method.Li98, alloy=Alloy.Parent, configs=DEFAULT_CONFIGS):
        self.method = method
        self.alloy = alloy

        config = None
        with open(configs) as config_f:
            config = json.load(config_f, parse_float=np.float32)
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
        self.ae1 = config['austenite_limits']['ae1_value']
        self.ae3 = config['austenite_limits']['ae3_value']

        self.comp_parent = None
        self.comp_weld = None
        self.comp_mix = None
        self.get_compositions(config)

        if self.auto_ms_bs_calc:
            self.auto_ms_bs()

        # TODO: Need to check if Ae available or can be calculated

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

        self.comp_parent = np.zeros(len(c_parent), dtype={'names': ['name', 'symbol', 'weight'],
                                                          'formats': [(np.str_, 10), (np.str_, 4), np.float32]})
        self.comp_weld = np.zeros(len(c_weld), dtype={'names': ['name', 'symbol', 'weight'],
                                                      'formats': [(np.str_, 10), (np.str_, 4), np.float32]})
        self.comp_mix = np.zeros(len(c_mix), dtype={'names': ['name', 'symbol', 'weight'],
                                                    'formats': [(np.str_, 10), (np.str_, 4), np.float32]})

        # iterate over all 3 lists at once and store them in the np.ndarray
        for i, (e_p, e_w, e_m) in enumerate(zip(c_parent, c_weld, c_mix)):
            self.comp_parent[i] = (e_p['name'], e_p['symbol'], e_p['value'])
            self.comp_weld[i] = (e_w['name'], e_w['symbol'], e_w['value'])
            self.comp_mix[i] = (e_m['name'], e_m['symbol'], e_m['value'])

    def auto_ms_bs(self) -> None:
        """We simply store the class variables bs_temp and ms_temp by doing the calculations."""
        self.bs_temp = self.get_bs()
        self.ms_temp = self.get_ms()

    def get_bs(self) -> np.float:
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

    def get_ms(self) -> np.float:
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

    def __str__(self):
        parent_t = PrettyTable(self.comp_parent.dtype.names)
        for row in self.comp_parent:
            parent_t.add_row(row)
        parent_t.align['name'] = 'l'
        parent_t.align['symbol'] = 'l'
        parent_t.align['weight'] = 'r'

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
        """.format(
            'Method:', self.method.name, 'Alloy:', self.alloy.name,
            'Nucleation Start:', self.nuc_start, 'Nucleation End:', self.nuc_finish,
            'Type:', self.grain_type, 'Value: ', self.grain_size,
            'Xfe:', self.xfe, 'Cf:', self.cf, 'Ceut:', self.ceut,
            'MS Temperature:', self.ms_temp, 'MS Undercool: ', self.ms_undercool,
            'BS Temperature: ', self.bs_temp,
            'Ae1:', self.ae1, 'Ae3:', self.ae3,
            parent_t
        )
