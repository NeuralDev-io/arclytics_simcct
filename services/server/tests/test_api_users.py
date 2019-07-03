# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'

"""test_api_users.py: 

{Description}
"""

import json
import unittest

from tests.test_api_base import BaseTestCase


class TestUserService(BaseTestCase):
    """Tests for the User API service."""
    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        res = self.client.get('/users/ping')
        data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('pong', data['message'])


if __name__ == '__main__':
    unittest.main()
