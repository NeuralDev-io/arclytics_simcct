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

import numpy as np
from typing import Union
from prettytable import PrettyTable

from .utilities import Method, ConfigurationError
from .ae3_utilities import ae3_single_carbon, ae3_multi_carbon
from .periodic import PeriodicTable


class SimConfiguration(object):
    """The SimConfiguration instance stores all the required arguments needed
    to simulate the Time-Temperature Transformation or the Cooling Curve
    Transformation. It also has methods to calculate some of these arguments
    automatically based on the Li '98 or Kirkaldy '83 equations as aggregated
    by Dr. Bendeich.
    """

    def __init__(self, configs: dict = None, compositions: list = None):
        if compositions is not None:
            self.comp = self.get_compositions(compositions)
            if self.comp is False:
                raise ConfigurationError('Compositions conversion error.')

        if configs is not None:
            self.method = (
                Method.Li98
                if configs['method'] == 'Li98' else Method.Kirkaldy83
            )

            self.nuc_start = configs['nucleation_start'] / 100
            self.nuc_finish = configs['nucleation_finish'] / 100
            self.grain_size = configs['grain_size']
            self.auto_calc_ms = configs['auto_calculate_ms']
            self.ms_temp = configs['ms_temp']
            self.ms_rate_param = configs['ms_rate_param']
            self.auto_calc_bs = configs['auto_calculate_bs']
            self.bs_temp = configs['bs_temp']
            self.auto_calc_ae = configs['auto_calculate_ae']
            self.ae1 = configs['ae1_temp']
            self.ae3 = configs['ae3_temp']
            self.temp_peak = configs['start_temp']
            self.cct_cooling_rate = configs['cct_cooling_rate']

            self.ae_check = False
            if self.ae1 > 0 and self.ae3 > 0:
                self.ae_check = True

            # We need Xfe in simulation calculations and we have defined a cf
            # that is set to 0.012 because that's what Dr. Bendeich thinks works

            self.xfe, self.eutectic_comp = self.xfe_method2(
                compositions, self.ae1
            )

        if self.ae1 < 0.0 or self.ae3 < 0.0:
            raise ConfigurationError('Ae1 and Ae3 temperatures not yet set.')
        if self.ms_temp < 0.0 or self.bs_temp < 0.0:
            raise ConfigurationError('MS and BS temperatures not yet set.')

    def auto_ms(self) -> None:
        """
        We simply store the class variables ms_temp by doing the calculations.
        """
        self.ms_temp = self.get_ms(self.method, self.comp)
        self.ms_rate_param = self.get_ms_alpha(self.comp)

    def auto_bs(self) -> None:
        """
        We simply store the class variables bs_temp by doing the calculations.
        """
        self.bs_temp = self.get_bs(self.method, self.comp)

    def auto_ae1_ae3(self) -> None:
        """Calculate the austenite values based on composition automatically."""
        # validate the Austenite values have been generated and it will not
        # crash the application
        self.ae_check = True
        self.ae1, self.ae3 = self.calc_ae1_ae3(self.comp)

    @staticmethod
    def get_compositions(comp_list: list = None) -> Union[np.ndarray, bool]:
        """
        We get the compositions from the list passed and extract the
        compositions as a list from parent, weld, and mix. We then store
        them as a Structured numpy.ndarray with ('name', 'symbol', 'weight')
        record types.
        Args:
            comp_list: a Dict of composition elements and weights with the key
                       being the element's atomic number.

        Returns:
            A structured numpy.ndarray with the weights and names.
        """
        comp = np.zeros(
            len(comp_list), dtype=[('symbol', 'U2'), ('weight', np.float16)]
        )

        # 2019-08-04: Update by andrew@neuraldev.io
        # We add a special condition where we ensure that 'C' and 'Fe' are
        # always the first and last element in our `comp` structured 1-D numpy
        # array. This is necessary because some of the other elements downstream
        # in the algorithm assume that 'C' and 'Fe' are first and last and we
        # cannot ensure that the `comp_list` or API client data will follow
        # this necessary step.

        # We need to make sure these are inserted and appended at beginning and
        # end respectively as it is assumed later.
        c_weight = None
        fe_weight = None

        # Use a special exterior index to ensure we don't add an empty space
        # when we skip enumerated numbers (if using enumerate()) which, when
        # skipping by
        idx = 1
        # iterate over lists at once and store them in the np.ndarray
        for e in comp_list:
            s = e['symbol']

            # We skip out if we hit 'C' or 'Fe' so we can add them later.
            if s == PeriodicTable.C.name:
                c_weight = e['weight']
                continue

            if s == PeriodicTable.Fe.name:
                fe_weight = e['weight']
                continue

            # Using the pt 1-to-1 mapping validates that the name is exactly
            # as we expect it. Will raise a KeyError exception if symbol names
            # don't match. We return False and check it later.
            try:
                elem_symbol = PeriodicTable[s].name
            except KeyError:
                raise ConfigurationError('Element Symbol Error.')
            comp[idx] = (elem_symbol, e['weight'])
            idx = idx + 1

        # Now we add carbon and iron at the beginning and end respectively
        comp[0] = (PeriodicTable.C.name, c_weight)
        comp[-1] = (PeriodicTable.Fe.name, fe_weight)
        return comp

    # TODO(andrew@neuraldev.io -- Sprint 6): Do some validation for these
    #  and return a tuple instead (float, error)
    @staticmethod
    def get_bs(method: Method = None, comp: np.ndarray = None) -> float:
        """
        Do the calculation based on Li98 or Kirkaldy 83 method and return
        the MS temperature.
        """
        # ensure we are getting the value and not the list by using index 0
        c = comp[comp['symbol'] == PeriodicTable.C.name]['weight'][0]
        mn = comp[comp['symbol'] == PeriodicTable.Mn.name]['weight'][0]
        ni = comp[comp['symbol'] == PeriodicTable.Ni.name]['weight'][0]
        cr = comp[comp['symbol'] == PeriodicTable.Cr.name]['weight'][0]
        mo = comp[comp['symbol'] == PeriodicTable.Mo.name]['weight'][0]
        si = comp[comp['symbol'] == PeriodicTable.Si.name]['weight'][0]

        if method != Method.Li98 and method != Method.Kirkaldy83:
            return -1

        if method == Method.Kirkaldy83:
            # Eqn [30] in Kirkaldy defined 1983 paper
            return (
                656 - (58 * c) - (35 * mn) - (75 * si) - (15 * ni) -
                (34 * cr) - (41 * mo)
            )

        # By default, we return Method.Li98
        # Eqn [24] in paper. Li modified from Kirkaldy.
        return (
            637.0 - (58 * c) - (35 * mn) - (15 * ni) - (34 * cr) - (41 * mo)
        )

    @staticmethod
    def get_ms(method: Method = None, comp: np.ndarray = None) -> float:
        """
        Do the calculation based on Li98 or Kirkaldy83 method and return the
        MS temperature.
        """
        # ensure we are getting the value and not the list by using index 0
        c = comp[comp['symbol'] == PeriodicTable.C.name]['weight'][0]
        mn = comp[comp['symbol'] == PeriodicTable.Mn.name]['weight'][0]
        ni = comp[comp['symbol'] == PeriodicTable.Ni.name]['weight'][0]
        cr = comp[comp['symbol'] == PeriodicTable.Cr.name]['weight'][0]
        mo = comp[comp['symbol'] == PeriodicTable.Mo.name]['weight'][0]
        co = comp[comp['symbol'] == PeriodicTable.Co.name]['weight'][0]
        si = comp[comp['symbol'] == PeriodicTable.Si.name]['weight'][0]

        if method != Method.Li98 and method != Method.Kirkaldy83:
            return -1

        if method == Method.Kirkaldy83:
            # Eqn [31] in Kirkaldy 1983 paper
            return (
                561 - (474 * c) - (33.0 * mn) - (17.0 * ni) - (17.0 * cr) -
                (21.0 * mo)
            )

        # By default we return Method.Li98
        # Eqn [25] in paper by Kung and Raymond
        return (
            539 - (423 * c) - (30.4 * mn) - (17.7 * ni) - (12.1 * cr) -
            (7.5 * mo) + (10.0 * co) - (7.5 * si)
        )

    @staticmethod
    def get_ms_alpha(comp: np.ndarray = None) -> float:
        c = comp['weight'][comp['symbol'] == PeriodicTable.C.name][0]
        mn = comp['weight'][comp['symbol'] == PeriodicTable.Mn.name][0]
        ni = comp['weight'][comp['symbol'] == PeriodicTable.Ni.name][0]
        cr = comp['weight'][comp['symbol'] == PeriodicTable.Cr.name][0]
        mo = comp['weight'][comp['symbol'] == PeriodicTable.Mo.name][0]

        return (
            0.0224 - (0.0107 * c) - (0.0007 * mn) - (0.00005 * ni) -
            (0.00012 * cr) - (0.0001 * mo)
        )

    @staticmethod
    def calc_ae1_ae3(comp: np.ndarray = None) -> (np.float, np.float):
        c = comp[comp['symbol'] == PeriodicTable.C.name]['weight'][0]
        ni = comp[comp['symbol'] == PeriodicTable.Ni.name]['weight'][0]
        si = comp[comp['symbol'] == PeriodicTable.Si.name]['weight'][0]
        w = comp[comp['symbol'] == PeriodicTable.W.name]['weight'][0]
        mn = comp[comp['symbol'] == PeriodicTable.Mn.name]['weight'][0]
        cr = comp[comp['symbol'] == PeriodicTable.Cr.name]['weight'][0]
        # `as` is a keyword you can't use so must use `_as`
        _as = comp[comp['symbol'] == PeriodicTable.As.name]['weight'][0]
        mo = comp[comp['symbol'] == PeriodicTable.Mo.name]['weight'][0]
        # Do the calculations
        # 1. Equations of Andrews (1965)
        ae1 = (
            723.0 - (16.9 * ni) + (29.1 * si) + (6.38 * w) - (10.7 * mn) +
            (16.9 * cr) + (290 * _as)
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
        ae3 = ae3_single_carbon(comp.copy(), c)
        return ae1, ae3 - 273

    def xfe_method2(
            self,
            comp_list: list = None,
            ae1: np.float = None,
            cf: np.float = 0.012,
            plot: bool = False
    ) -> (np.float, np.float):
        """Second method for estimating Xfe using parra-equilibrium methodology
        to predict  the Ae3 values with increasing carbon content. To find
        the intercept with Ae1 (from simplified method) to determine the
        eutectic carbon content wt%. With this value and a suitable estimate
        of the ferrite carbon content (~0.02 wt%). With these limits ant the
        current alloy composition the lever rule can be used to determine the
        equilibrium phase fraction

        Returns:

        """
        # Just to keep the name shorter.
        wt = self.get_compositions(comp_list)
        # store results of each iteration of Carbon

        results_mat = np.zeros((1000, 22), dtype=np.float32)
        # reserve the initial carbon wt% as the main routine is passing back
        # another value despite being set "ByVal"
        wt_c = wt['weight'][wt['symbol'] == PeriodicTable.C.name][0]

        # Find Ae3 for array of Carbon contents form 0.00 to 0.96 wt%
        # UPDATE wt, Results to CALL Ae3MultiC(wt, Results)
        ae3_multi_carbon(wt, results_mat)

        # TODO(andrew@neuraldev.io): Figure out a way to get the `results_mat`
        #  to the View method so that it can be returned to plot.
        # We can view the Ae3 plot with a call to the following
        # CALL Ae3Plot(results_mat, self.ae1, wt_c)
        if plot:
            # TODO(andrew@neuraldev.io): Should probably consider returning
            #  this as a dict with the graph lines consistent with the other
            #  simulation methods.
            return results_mat

        eutectic_composition_carbon = 0.0
        # Find the Ae3-Ae1 intercept Carbon content (Eutectic composition)
        if ae1 > 0:
            for i in range(1000):
                if results_mat[i, 1] <= ae1:
                    eutectic_composition_carbon = results_mat[i, 0]
                    break

        # Now calculate the important bit the Xfe equilibrium phase fraction
        # of Ferrite
        tie_length = eutectic_composition_carbon - cf
        lever1 = tie_length - wt_c
        ferrite_phase_frac = lever1 / tie_length

        # Note shorthands are: `xfe` and `eutectic_comp`
        return ferrite_phase_frac, eutectic_composition_carbon

    def __str__(self) -> str:
        return """
-------------------------------------------------
PHASE SIMULATION CONFIGURATIONS
-------------------------------------------------
{:30}{}
Transformation Definitions:
  {:28}{:.4f}
  {:28}{:.4f}
Grain Size:
  {:28}{:6.4f}
Transformation Temp. Limits:
  {:28}{}
  {:28}{:.4f}
  {:28}{}
  {:28}{:.4f}
Austenite Limits: 
  {:28}{}
  {:28}{:.4f}
  {:28}{:.4f}

-------------------------------------------------
        """.format(
            'Method:', self.method.name, 'Nucleation Start:', self.nuc_start,
            'Nucleation End:', self.nuc_finish, 'Value: ', self.grain_size,
            'Auto Calculate:', self.auto_calc_ms, 'MS Temperature:',
            self.ms_temp, 'Auto Calculate:', self.auto_calc_bs,
            'BS Temperature: ', self.bs_temp, 'Auto Calculate:',
            self.auto_calc_ae, 'Ae1:', self.ae1, 'Ae3:', self.ae3
        )
