# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
# 
# Attributions: 
# [1] 
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.13'
"""test_api_sim_configs.py: 

{Description}
"""

import unittest

from tests.test_api_base import BaseTestCase


class TestSimConfigurations(BaseTestCase):

    def test_on_compositions_change(self):

        # - Combined method for changing the sessions compositions
        # - Check if the compositions are valid
        # -
        # - Check if auto calculate is selected for ms_bs, ae, or xfe
        # - Compute for the calculations that auto_calculate_x is True
        # - Save the value to session store.
        # - Return the values
        pass

    def test_auto_update_ms_bs(self):

        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.
        #
        # - If they have a session store of compositions, use that.
        # - Check if the compositions has valid elements required.
        # - Compute the MS and BS
        # - Update the MS and BS for session store
        # - Return the values
        pass

    def test_auto_update_ae(self):
        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.
        #
        # - If they have a session store of compositions, use that.
        # - Check if the compositions has valid elements required.
        # - Compute the Ae1 and Ae3
        # - Update the Ae1 and Ae3 for session store
        # - Return the values
        pass

    def test_auto_update_xfe(self):
        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.
        #
        # - If they have a session store of compositions, use that.
        # - Check if the compositions has valid elements required.
        # - Compute the xfe (and others) values
        # - Update the xfe (and others) values for session store
        # - Return the values
        pass


if __name__ == '__main__':
    unittest.main()
