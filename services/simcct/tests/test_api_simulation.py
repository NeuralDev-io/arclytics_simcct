# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.17'
"""test_api_simulation.py: 

{Description}
"""
import os
import unittest
from pathlib import Path

from flask import json
from mongoengine import get_db

from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login
from sim_api.extensions.SimSession import SimSessionService
from sim_api.models import User, AlloyStore, Configuration
from sim_api.schemas import ConfigurationsSchema, AlloyStoreSchema
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'

with open(_TEST_CONFIGS_PATH, 'r') as f:
    test_json = json.load(f)


class TestSimulationService(BaseTestCase):
    _email = None
    _user_pw = 'IMissThor!!!'
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        assert app.config['TESTING'] is True

        cls.user = User(
            **{
                'email': 'jane@culver.edu.us',
                'first_name': 'Jane',
                'last_name': 'Foster',
            }
        )
        cls.user.set_password(cls._user_pw)
        cls.user.verified = True

        configs = ConfigurationsSchema().load(test_json['configurations'])
        store_dict = {
            'alloy_option': 'single',
            'alloys': {
                'parent': {
                    'name': 'Arc_Stark',
                    'compositions': test_json['compositions']
                },
                'weld': None,
                'mix': None
            }
        }
        alloy_store = AlloyStoreSchema().load(store_dict)

        cls.user.last_alloy_store = AlloyStore(**alloy_store)
        cls.user.last_configuration = Configuration(**configs)

        cls.user.save()
        cls._email = cls.user.email

        mongo = get_db('default')
        user = mongo.users.find_one({'email': 'jane@culver.edu.us'})
        assert user is not None

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def login_client(self, client):
        """Set up a User for the simulation."""
        test_login(client, self._email, self._user_pw)

        session_store: dict = SimSessionService().load_session()
        configs: dict = session_store['configurations']
        alloy_store: dict = session_store['alloy_store']

        return configs, alloy_store

    def test_simulate_no_prev_configs(self):
        """Ensure that if they have no previous configurations set it fails."""
        with app.test_client() as client:
            # We login to get a cookie
            _, _ = self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                    environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                session['simulation'] = None
            with client.session_transaction(
                    environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ):
                # At this point the session transaction has been updated so
                # we can check the session within the context
                session_store = SimSessionService().load_session()
                self.assertIsInstance(session_store, str)
                self.assertEqual(session_store, 'Session is empty.')

            res = client.get(
                '/api/v1/sim/simulate',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Cannot retrieve data from Session store.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertStatus(res, 500)

    def test_simulate_no_prev_alloy(self):
        """Ensure that if the user does not have a previous alloy it fails."""
        # configs = ConfigurationsSchema().load(test_json['configurations'])
        with app.test_client() as client:
            # We login to get a cookie
            _, _ = self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                    environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                session_store = json.loads(session['simulation'])
                session_store['alloy_store']['alloys']['parent'] = None
                ser_session_data = json.dumps(session_store)
                prefix = SimSessionService.SESSION_PREFIX
                session[prefix] = ser_session_data

            res = client.get(
                '/api/v1/sim/simulate',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'No previous session alloy was set.'
            )
            self.assert404(res)
            self.assertEqual(data['status'], 'fail')

    def test_simulate_with_login(self):
        """Ensure there is a successful simulation get request."""
        with app.test_client() as client:
            self.login_client(client)

            # MUST have AE and MS/BS > 0.0 before we can run simulate
            res = client.get(
                '/api/v1/sim/configs/ae',
                content_type='application/json'
            )
            self.assert200(res)

            res = client.get(
                '/api/v1/sim/configs/ms',
                content_type='application/json'
            )
            self.assert200(res)
            res = client.get(
                '/api/v1/sim/configs/bs',
                content_type='application/json'
            )
            self.assert200(res)

            # Now we can run
            res = client.get(
                '/api/v1/sim/simulate',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertFalse(data.get('message', None))
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            self.assertEqual(
                len(data['data']['CCT']['ferrite_nucleation']['time']),
                len(data['data']['CCT']['ferrite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['ferrite_completion']['time']),
                len(data['data']['CCT']['ferrite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['pearlite_nucleation']['time']),
                len(data['data']['CCT']['pearlite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['pearlite_completion']['time']),
                len(data['data']['CCT']['pearlite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['bainite_nucleation']['time']),
                len(data['data']['CCT']['bainite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['bainite_completion']['time']),
                len(data['data']['CCT']['bainite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['martensite']['time']),
                len(data['data']['CCT']['martensite']['temp'])
            )

    # def test_simulate_plotting(self):
    #     with app.test_client() as client:
    #         self.login_client(client)
    #
    #         res = client.get(
    #             '/simulate',
    #             headers={'Authorization': f'Bearer {self.token}'},
    #             content_type='application/json'
    #         )
    #         data = json.loads(res.data.decode())
    #         self.assert200(res)
    #         self.assertTrue(data['data'])


if __name__ == '__main__':
    unittest.main()
