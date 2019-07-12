# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_base.py
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
__date__ = '2019.07.12'
"""test_api_base.py: 

{Description}
"""


from unittest import TestCase

from sim_api import create_app

app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('users_api.config.TestingConfig')
        return app

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        # Drop database
        pass
