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
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)


class TestUserService(BaseTestCase):
    """Tests for the User API service."""
    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        res = self.client.get('/users/ping')
        data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('pong', data['message'])

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'codeninja55',
                    'email': 'andrew@neuraldev.io'
                }),
                content_type='application/json'
            )
            logger.debug(response)
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('andrew@neuraldev.io was added', data['message'])
            self.assertIn('success', data['status'])

    def post(self):
        pass


if __name__ == '__main__':
    unittest.main()
