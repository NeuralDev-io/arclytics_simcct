# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_last_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.08.11'

import os
import unittest
from copy import deepcopy
from pathlib import Path

from flask import current_app as app
from flask import json
from mongoengine import get_db

from sim_api.models import AdminProfile, User, UserProfile
from tests.test_api_base import BaseTestCase
from tests.test_utilities import test_login
from arc_logging import AppLogger

logger = AppLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'sim_configs.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    _TEST_JSON = json.load(f)

# Use these as they are valid and make copies and change the dict if you want
# to invalidate the data that is sent in the request.
CONFIGS = _TEST_JSON['configurations']
COMP = _TEST_JSON['compositions']
ALLOY_STORE = {
    'alloy_option': 'single',
    'alloys': {
        'parent': {
            'name': 'Pym Alloy',
            'compositions': COMP
        },
        'weld': None,
        'mix': None
    }
}
RESULTS = _TEST_JSON['simulation_results']


class TestLastSimulation(BaseTestCase):
    _email = None
    _tony_pw = 'IAmIronMan!!!'
    mongo = None

    def setUp(self) -> None:
        assert app.config['TESTING'] is True
        self.mongo = get_db('default')

        # Tony is an admin
        self.tony = User(
            **{
                'email': 'ironman@avengers.com',
                'first_name': 'Tony',
                'last_name': 'Stark'
            }
        )
        self.tony.set_password(self._tony_pw)
        self.tony.verified = True
        self.tony.profile = UserProfile(
            **{
                'aim': 'Save the world',
                'highest_education': 'Genius',
                'sci_tech_exp': 'Invented J.A.R.V.I.S.',
                'phase_transform_exp': 'More than you'
            }
        )
        self.tony.admin_profile = AdminProfile(
            **{
                'position': 'Billionaire Playboy Philanthropist',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        self.tony.disable_admin = False
        self.tony.save()
        user_tony = self.mongo.users.find_one(
            {'email': 'ironman@avengers.com'}
        )
        assert user_tony is not None
        assert user_tony['admin'] is True
        self._email = self.tony.email

    def tearDown(self) -> None:
        db = get_db('default')
        self.assertTrue(db.name, 'arc_test')
        db.users.drop()

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def test_create_last_no_token(self):
        with app.test_client() as client:
            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_create_last_empty_json(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_missing_configurations(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            # self.assertEqual(
            #     data['message'], 'Missing Configurations in payload.'
            # )
            # self.assertEqual(data['status'], 'fail')
            # self.assert400(res)
            self.assertEqual(data['message'], 'Saved Last Simulation Data.')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)

    def test_create_last_missing_alloy_store(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps({
                    'is_valid': True,
                    'configurations': CONFIGS
                }),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Saved Last Simulation Data.')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)

    def test_create_last_invalid_configs_missing(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            configs = deepcopy(_TEST_JSON['configurations'])

            configs.pop('method')
            configs.pop('grain_size')

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': configs,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = "{'method': ['A method is required.']}"
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Model schema validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_configs_bad_method(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            configs = deepcopy(CONFIGS)
            configs['method'] = 'KirkaldyAndLi2019'

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': configs,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = "{'method': ['Must be one of: Li98, Kirkaldy83.']}"
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Model schema validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_configs_bad_nuc_start(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            configs = deepcopy(CONFIGS)
            configs['nucleation_start'] = -1

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': configs,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = (
                "{'nucleation_start': ['Nucleation start must be "
                "more than 0.0.']}"
            )
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Model schema validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_configs_bad_nuc_finish(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            configs = deepcopy(CONFIGS)
            configs['nucleation_finish'] = 101

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': configs,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = (
                "{'nucleation_finish': ['Nucleation finish cannot be more "
                "than 99.99.']}"
            )
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Model schema validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_configs_negative_trans_temps(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            configs = deepcopy(CONFIGS)
            configs['ms_temp'] = -1

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': configs,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = ("{'ms_temp': ['Cannot be negative.']}")
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Model schema validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_alloy_option(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)

            alloy_store = {
                'alloy_option': 'random',
                'alloys': {
                    'parent': {
                        'name': 'Pym Alloy',
                        'compositions': COMP
                    },
                    'weld': None,
                    'mix': None
                }
            }

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = "{'alloy_option': ['Must be one of: single, mix.']}"
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Model schema validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_alloy_missing_elem(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            comp = deepcopy(COMP)
            del comp[-1]

            alloy_store = {
                'alloy_option': 'parent',
                'alloys': {
                    'parent': {
                        'name': 'Pym Alloy',
                        'compositions': comp
                    },
                    'weld': None,
                    'mix': None
                }
            }

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['error'], "Missing elements ['Fe']")
            self.assertEqual(data['message'], "Missing element error.")
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_alloy_bad_elem(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            comp = deepcopy(COMP)
            comp.append({'symbol': 'Vb', 'weight': 0.0})

            alloy_store = {
                'alloy_option': 'parent',
                'alloys': {
                    'parent': {
                        'name': 'Pym Alloy',
                        'compositions': comp
                    },
                    'weld': None,
                    'mix': None
                }
            }

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = (
                'ValidationError (Element) (Field does not match a valid '
                'element symbol in the Periodic Table: ["symbol"])'
            )
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], "Invalid element symbol error.")
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_invalid_alloy_bad_elem_weight(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)
            comp = deepcopy(COMP)
            comp.append({'symbol': 'Li', 'weight': -1})

            alloy_store = {
                'alloy_option': 'parent',
                'alloys': {
                    'parent': {
                        'name': 'Pym Alloy',
                        'compositions': comp
                    },
                    'weld': None,
                    'mix': None
                }
            }

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = "ValidationError (Weight) (Weight must be more than 0.0.)"
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], "Invalid element weight error.")
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_last_alloy_invalid_configs(self):
        """Ensure we can save a last configuration that is invalid."""
        with app.test_client() as client:
            test_login(client, self.tony.email, self._tony_pw)
            configs = deepcopy(CONFIGS)
            configs['is_valid'] = False
            configs['nucleation_start'] = -1

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': False,
                        'configurations': configs,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': {}
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Saved Invalid Last Simulation Data.'
            )
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            user = self.tony
            user.reload()

            self.assertDictEqual(user.last_configuration, configs)
            self.assertDictEqual(user.last_alloy_store, ALLOY_STORE)
            self.assertDictEqual(user.last_simulation_results, {})

    def test_create_last_alloy_invalid_alloys(self):
        """Ensure we can save a last configuration that is invalid."""
        with app.test_client() as client:
            test_login(client, self.tony.email, self._tony_pw)
            comp = deepcopy(COMP)
            # Carbon can't be more than 0.8 which is invalid
            comp[0]['weight'] = 0.9
            alloy_store: dict = {
                'alloy_option': 'single',
                'alloys': {
                    'parent': {
                        'name': 'Pym Alloy',
                        'compositions': comp
                    },
                    'weld': None,
                    'mix': None
                }
            }

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': False,
                        'configurations': {},
                        'alloy_store': alloy_store,
                        'simulation_results': {}
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Saved Invalid Last Simulation Data.'
            )
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            user = self.tony
            user.reload()

            self.assertDictEqual(user.last_alloy_store, alloy_store)
            self.assertDictEqual(user.last_configuration, {})
            self.assertDictEqual(user.last_simulation_results, {})

    def test_create_last_alloy_configs(self):
        with app.test_client() as client:
            _ = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Saved Last Simulation Data.')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            user = self.tony
            user.reload()

            self.assertDictEqual(user.last_configuration, CONFIGS)

    def test_get_detail_last_no_token(self):
        with app.test_client() as client:
            res = client.get(
                '/v1/sim/user/last/simulation',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_get_detail_empty_no_last_configs(self):
        with app.test_client() as client:
            user = User(
                **{
                    'first_name': 'Janet',
                    'last_name': 'van Dyne',
                    'email': 'janet@pymtechnologies.com'
                }
            )
            user.set_password('Subatomic!')
            user.verified = True
            user.save()

            _ = test_login(client, user.email, 'Subatomic!')

            res = client.get(
                '/v1/sim/user/last/simulation',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'],
                'User does not have a last configurations or alloy store.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert404(res)
            user.delete()

    def test_get_detail_empty_no_last_alloy(self):
        with app.test_client() as client:
            user = User(
                **{
                    'first_name': 'Janet',
                    'last_name': 'van Dyne',
                    'email': 'janet@pymtechnologies.com'
                }
            )
            user.set_password('Subatomic!')
            user.verified = True
            user.last_configuration = CONFIGS
            user.save()

            test_login(client, user.email, 'Subatomic!')

            res = client.get(
                '/v1/sim/user/last/simulation',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(
                data['data']['last_configuration']['grain_size'], 8.0
            )
            user.delete()

    def test_get_last_alloy_invalid_save(self):
        """Ensure we can get a last configuration that is invalid."""
        with app.test_client() as client:
            test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': False,
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': {}
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Saved Invalid Last Simulation Data.'
            )
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            user = self.tony
            user.reload()

            configs = deepcopy(CONFIGS)
            configs.update({'is_valid': False})

            self.assertDictEqual(user.last_alloy_store, ALLOY_STORE)
            self.assertDictEqual(user.last_configuration, configs)
            self.assertDictEqual(user.last_simulation_results, {})

            res = client.get(
                '/v1/sim/user/last/simulation',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data.get('data', None))
            self.assertDictEqual(data['data']['last_configuration'], configs)

    def test_get_detail_last_success(self):
        with app.test_client() as client:
            test_login(client, self.tony.email, self._tony_pw)

            post_res = client.post(
                '/v1/sim/user/last/simulation',
                data=json.dumps(
                    {
                        'is_valid': True,
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(post_res.data.decode())
            self.assertEqual(data['message'], 'Saved Last Simulation Data.')

            res = client.get(
                '/v1/sim/user/last/simulation',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data.get('data', None))
            self.assertDictEqual(data['data']['last_configuration'], CONFIGS)

            _name = data['data']['last_alloy_store']['alloys']['parent']['name'
                                                                         ]
            self.assert200(res)
            self.assertEqual(
                data['data']['last_alloy_store']['alloys']['parent']['name'],
                _name
            )


if __name__ == '__main__':
    unittest.main()
