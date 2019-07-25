# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_session.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__date__ = '2019.07.12'

import os
import requests
import unittest
from pathlib import Path

from bson import ObjectId
from pymongo import MongoClient
from flask import current_app, session, json

from sim_app.app import BASE_DIR
from tests.test_api_base import BaseTestCase

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSessionService(BaseTestCase):
    users_host = os.environ.get('USERS_HOST')
    base_url = f'http://{users_host}'
    _id = None

    @classmethod
    def setUpClass(cls) -> None:
        """We just set up Jane as a user in the database and then store her
        credentials so we can use it later.
        """
        resp = requests.post(
            url=f'{cls.base_url}/auth/register',
            json={
                'email': 'jane@culver.edu.us',
                'first_name': 'Jane',
                'last_name': 'Foster',
                'password': 'IDumpedThor'
            }
        )
        data = resp.json()
        cls.token = data.get('token')

        user_resp = requests.get(
            f'{cls.base_url}/auth/status',
            headers={
                'Content-type': 'application/json',
                'Authorization': f'Bearer {cls.token}'
            }
        )
        data = user_resp.json()
        cls.user_id = data.get('data')['_id']
        cls._id = cls.user_id

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete Jane so she's not registered again."""
        # We make a conn to Mongo
        mongo = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
        # user = mongo['arc_dev'].users.find_one({'_id': ObjectId(cls._id)})
        # And just delete Jane from the db
        mongo.arc_dev.users.delete_one({'_id': ObjectId(cls._id)})

    def login_jane(self, client):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        login_res = client.post(
            '/session/login',
            data=json.dumps(
                {
                    '_id': self.user_id,
                    'last_configurations': test_json['configurations'],
                    'last_compositions': {
                        'alloy': {
                            'name': 'Arc_Stark',
                            'compositions': test_json['compositions']
                        }
                    }
                }
            ),
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='application/json'
        )
        data = json.loads(login_res.data.decode())
        self.assertEqual(data['message'], 'User session initiated.')
        self.assertEqual(data['status'], 'success')
        self.assertEqual(session.get(f'{self.user_id}:token'), self.token)
        self.assertEqual(session.get(f'{self.token}:user'), self.user_id)
        self.assertTrue(session.get(f'{self.token}:configurations'))
        self.assertTrue(session.get(f'{self.token}:alloy'))

    def test_session_user_ping(self):
        """Just a sanity check test that there is connection to users-server."""
        with current_app.test_client() as client:
            res = client.get('/users/ping', content_type='application/json')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['message'], 'pong')
            self.assertEqual(data['status'], 'success')

    def test_session_post(self):
        """Ensure we can use the requests library to make registration/login
        to the users-server and get the correct responses.
        """
        with self.app.test_client() as client:
            # Made a helper method that was being reused which does the test for
            # this particular test.
            self.login_jane(client)

    def test_login_session_empty_post_data(self):
        with self.app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assert400(login_res)

    def test_login_session_no_user_id(self):
        with self.app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps({'not_id': 'ThisWontBeRead'}),
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(
                data['message'], 'User ObjectId must be provided.'
            )
            self.assert401(login_res)

    def test_login_session_invalid_objectid_user_id(self):
        with self.app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps({'_id': 'NotAValidObjectIdType'}),
                headers={'Authorization': f'Bearer JustATest!'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(
                data['message'], 'User ObjectId must be provided.'
            )
            self.assert401(login_res)

    def test_login_session_no_token(self):
        with self.app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps({'_id': self.user_id}),
                headers={'Authorization': f'Bearer '},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(data['message'], 'Invalid JWT token in header.')
            self.assert401(login_res)

    def test_login_user_with_no_configurations(self):
        """Ensure that if the user logged in without configurations it defaults
        to the empty configs.
        """
        _id = ObjectId()
        token = 'ThisIsOnlyATestingToken'
        with current_app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps({
                    '_id': str(_id),
                }),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            sess_saved = session.get(f'{str(token)}:configurations')
            self.assertEqual(sess_saved['method'], 'Li98')

    def test_login_user_with_invalid_configurations(self):
        """Ensure that if a user has an invalid config it fails."""
        _id = ObjectId()

        # Missing method and alloy which are both required.
        configs = {
            'is_valid': True,
            'grain_size': 8.0,
            'nucleation_start': 1.0,
            'nucleation_finish': 99.9,
            'auto_calculate_ms': True,
            'auto_calculate_bs': True,
            'ms_temp': 0.0,
            'ms_rate_param': 0.0168,
            'bs_temp': 0.0,
            'auto_calculate_ae': True,
            'ae1_temp': 0.0,
            'ae3_temp': 0.0,
            'start_temp': 900.0,
            'cct_cooling_rate': 10
        }
        token = 'ThisIsOnlyATestingToken'

        with current_app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'last_configurations': configs,
                        'last_compositions': {
                            'alloy': {
                                'name': '',
                                'compositions': []
                            }
                        }
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assert400(login_res)
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')
            sess_saved = session.get(f'{str(token)}:configurations')
            self.assertFalse(sess_saved)

    def test_login_user_with_configurations(self):
        """Ensure that if a user has an appropriate last_configurations then
        it is set appropriately.
        """
        configs = {
            'is_valid': True,
            'method': 'Li98',
            'alloy_type': 'parent',
            'grain_size': 8.0,
            'nucleation_start': 1.0,
            'nucleation_finish': 99.9,
            'auto_calculate_ms': True,
            'ms_temp': 0.0,
            'ms_rate_param': 0.0168,
            'auto_calculate_bs': True,
            'bs_temp': 0.0,
            'auto_calculate_ae': True,
            'ae1_temp': 0.0,
            'ae3_temp': 0.0,
            'start_temp': 900.0,
            'cct_cooling_rate': 10
        }

        with current_app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps(
                    {
                        '_id': str(self.user_id),
                        'last_configurations': configs,
                        'last_compositions': {
                            'alloy': {
                                'name': '',
                                'compositions': []
                            }
                        }
                    }
                ),
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            sess_saved = session.get(f'{str(self.token)}:configurations')
            self.assertEqual(sess_saved['method'], 'Li98')
            self.assertEqual(sess_saved['alloy_type'], 'parent')
            self.assertEqual(sess_saved['grain_size'], 8.0)
            self.assertEqual(sess_saved['auto_calculate_ms'], True)
            self.assertEqual(sess_saved['auto_calculate_bs'], True)
            self.assertEqual(sess_saved['auto_calculate_ae'], True)

    def test_login_user_with_invalid_compositions(self):
        """Ensure if the comp is invalid it fails."""
        configs = {
            'is_valid': True,
            'method': 'Li98',
            'alloy_type': 'parent',
            'grain_size': 8.0,
            'nucleation_start': 1.0,
            'nucleation_finish': 99.9,
            'auto_calculate_ms': True,
            'ms_temp': 0.0,
            'ms_rate_param': 0.0168,
            'auto_calculate_bs': True,
            'bs_temp': 0.0,
            'auto_calculate_ae': True,
            'ae1_temp': 0.0,
            'ae3_temp': 0.0,
            'start_temp': 900.0,
            'cct_cooling_rate': 10
        }
        e1 = {'name': 'carbon', 'weight': 0.044}
        e2 = {'name': 'manganese', 'weight': 1.73}

        with current_app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps(
                    {
                        '_id': str(self.user_id),
                        'token': self.token,
                        'last_configurations': configs,
                        'last_compositions': {
                            'alloy': {
                                'name': 'Random',
                                'compositions': [e1, e2]
                            }
                        }
                    }
                ),
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            self.assert400(login_res)
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')
            comp_store = session.get(f'{str(self.token)}:alloy')
            self.assertIsNone(comp_store)

    def test_login_user_with_compositions(self):
        """Ensure if the user a last_compositions it is added to Redis store."""
        e1 = {'symbol': 'C', 'weight': 0.044}
        e2 = {'symbol': 'Mn', 'weight': 1.73}
        e3 = {'symbol': 'Si', 'weight': 0.22}

        with current_app.test_client() as client:
            login_res = client.post(
                '/session/login',
                data=json.dumps(
                    {
                        '_id': str(self.user_id),
                        'token': self.token,
                        'last_configurations': {},
                        'last_compositions': {
                            'alloy': {
                                'name': 'Random',
                                'compositions': [e1, e2, e3]
                            }
                        }
                    }
                ),
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            comp_store = session.get(f'{str(self.token)}:alloy')
            self.assertTrue(comp_store['compositions'])
            stored_elem1 = comp_store['compositions'][0]
            stored_elem2 = comp_store['compositions'][1]
            stored_elem3 = comp_store['compositions'][2]
            self.assertEqual(stored_elem1['symbol'], e1['symbol'])
            self.assertEqual(stored_elem1['weight'], e1['weight'])
            self.assertEqual(stored_elem2['symbol'], e2['symbol'])
            self.assertEqual(stored_elem2['weight'], e2['weight'])
            self.assertEqual(stored_elem3['symbol'], e3['symbol'])
            self.assertEqual(stored_elem3['weight'], e3['weight'])

    # TODO(andrew@neuraldev.io): Need to fix the below tests as they are
    #  commented out because Logout does not seem to work cross-servers.
    def test_logout_user_invalid_token(self):
        """Ensure if we try to pass an invalid token it will not logout."""

        with self.app.test_client() as client:
            self.login_jane(client)
            logout_res = client.get(
                '/session/logout',
                headers={'Authorization': f'Bearer ThisWasNotTheUsersToken'},
                content_type='application/json'
            )
            data = json.loads(logout_res.data.decode())
            # self.assert401(logout_res)
            # self.assertEqual(data['status'], 'fail')
            # self.assertTrue(session.get(f'{self.user_id}:token') ==
            # self.token)
            # self.assertTrue(session.get('user'))
            # self.assertIsNone(session.get(f'{self.token}:configurations'))
            # self.assertIsNone(session.get(f'{self.token}:alloy'))

    def test_logout_user(self):
        """Successfully logged user out."""
        with self.app.test_client() as client:
            self.login_jane(client)
            logout_res = client.get(
                '/session/logout',
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            data = json.loads(logout_res.data.decode())
            self.assert200(logout_res)
            self.assertEqual(data['status'], 'success')
            # self.assertFalse(session.get(f'{self.user_id}:token') ==
            # self.token)
            # self.assertIsNone(session.get('user'))
            # self.assertIsNone(session.get(f'{self.token}:configurations'))
            # self.assertIsNone(session.get(f'{self.token}:alloy'))


if __name__ == '__main__':
    unittest.main()
