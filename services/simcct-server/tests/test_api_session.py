# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_session.py
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
"""test_api_session.py: 

{Description}
"""

import json
from tests.test_api_base import BaseTestCase


class TestSessionService(BaseTestCase):

    def test_session_user_ping(self):
        with self.client:
            res = self.client.get('/users/ping')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['message'], 'pong')
            self.assertEqual(data['status'], 'success')

    def test_session_post(self):
        pass

