# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_simulation.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.26'

"""test_simulation.py: 

{Description}
"""

import unittest
from pprint import pprint
import numpy as np
from simulation.simconfiguration import SimConfiguration
from simulation.ae3_utilities import *


class TestAe3(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_inst = SimConfiguration(debug=True)

    # def test_print(self):
    #     print(self.sim_inst)

    def test_ms(self):
        self.assertAlmostEqual(self.sim_inst.ms_temp, 464.1960, 4)

    def test_bs(self):
        self.assertAlmostEqual(self.sim_inst.bs_temp, 563.2380, 4)

    def test_ae1(self):
        self.assertAlmostEqual(self.sim_inst.ae1, 700.9020, 4)

    def test_con_wt_2_mol(self):
        wt = self.sim_inst.comp_parent.copy()
        wt['weight'][wt['name'] == 'carbon'] = 0.0
        wt['weight'][wt['name'] == 'iron'] = 0.0
        self.assertAlmostEqual(wt['weight'][wt['name'] == 'carbon'], 0.0, 6)
        self.assertAlmostEqual(wt['weight'][wt['name'] == 'iron'], 0.0, 6)
        x_vect = np.zeros(wt.shape[0], dtype=np.float64)
        yy_vect = np.zeros(wt.shape[0], dtype=np.float64)
        wt, x_vect, y = convert_wt_2_mol(wt, x_vect, yy_vect)
        logger.debug("wt:")
        logger.pprint(wt)
        logger.debug("x_vect:\n {}, \n\ny:\n {}".format(x_vect, y))

    # def test_ae3(self):
    #     self.assertAlmostEqual(self.sim_inst.ae3, 845.83796118, 4)

    # def test_xfe(self):
    #     self.assertAlmostEqual(self.sim_inst.xfe, 0.946210, 4)


if __name__ == '__main__':
    unittest.main()
