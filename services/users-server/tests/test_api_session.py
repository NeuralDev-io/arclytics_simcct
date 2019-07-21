# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_session.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.13'
"""test_api_session.py: 

{Description}
"""

import os
import json
import unittest
from pathlib import Path

from users_api.models.models import User, Configuration
from users_api.resources.auth import (
    async_register_session, SessionValidationError
)
from tests.test_api_base import BaseTestCase

_TEST_CONFIGS_PATH = Path(os.getcwd()) / 'tests' / 'sim_configs.json'


class TestSimCCTSession(BaseTestCase):
    """Test suite to test creating a session when logging in."""

    def test_register_session_with_login(self):
        """
        Ensure we are properly registered with simcct server using the async
        register method so we can get an appropriate response.
        """
        peter = User(
            email='spiderman@newavenger.io',
            first_name='Peter',
            last_name='Parker'
        )
        peter.set_password('SpideySenses')
        peter.save()

        token = peter.encode_auth_token(peter.id)
        simcct_res = async_register_session(peter, str(token))
        self.assertEqual(simcct_res['status'], 'success')
        self.assertEqual(simcct_res['message'], 'User session initiated.')
        self.assertTrue(simcct_res['session_id'])

    def test_register_session_multiple_login(self):
        """Ensure we have different session id's for different login."""
        peter = User(
            email='spiderman@newavenger.io',
            first_name='Peter',
            last_name='Parker'
        )
        peter.set_password('SpideySenses')
        peter.save()
        tony = User(
            email='tony@avengers.io', first_name='Tony', last_name='Stark'
        )
        tony.set_password('IAmIronMan')
        tony.save()

        token = peter.encode_auth_token(peter.id)
        petey_res = async_register_session(peter, str(token))
        token = peter.encode_auth_token(tony.id)
        tony_res = async_register_session(peter, str(token))

        self.assertEqual(petey_res['status'], 'success')
        self.assertEqual(petey_res['message'], 'User session initiated.')
        self.assertEqual(tony_res['status'], 'success')
        self.assertEqual(tony_res['message'], 'User session initiated.')
        self.assertNotEqual(petey_res['session_id'], tony_res['session_id'])

    def test_register_session_invalid_json_no_id(self):
        tony = User(
            email='tony@avengers.io', first_name='Tony', last_name='Stark'
        )
        tony.set_password('IAmIronMan')
        tony.save()

        token = tony.encode_auth_token(tony.id)

        with self.assertRaises(SessionValidationError):
            res = async_register_session("", str(token))

    def test_register_session_invalid_json_no_token(self):
        tony = User(
            email='tony@avengers.io', first_name='Tony', last_name='Stark'
        )
        tony.set_password('IAmIronMan')
        tony.save()

        with self.assertRaises(SessionValidationError):
            res = async_register_session(tony, "")

    def test_register_session_valid_configs(self):
        jane = User(
            email='jane@culver.edu.us', first_name='Jane', last_name='Foster'
        )
        jane.set_password('LadyAether')
        jane.save()

        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)
        test_configs = test_json['configurations']

        config_inst = Configuration(**test_configs)
        jane.last_configuration = config_inst
        jane.cascade_save()

        self.assertIsNotNone(jane.last_configuration)

        token = jane.encode_auth_token(jane.id)

        simcct_res = async_register_session(jane, str(token))
        self.assertEqual(simcct_res['status'], 'success')
        self.assertEqual(simcct_res['message'], 'User session initiated.')
        self.assertTrue(simcct_res['session_id'])


if __name__ == '__main__':
    unittest.main()
