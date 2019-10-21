# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.07.13'

import os
import unittest
from copy import deepcopy
from pathlib import Path

from bson import ObjectId
from flask import current_app as app
from flask import json
from mongoengine import DoesNotExist, get_db

from sim_api.models import (
    AdminProfile, AlloyStore, Configuration, SavedSimulation, User, UserProfile
)
from tests.test_api_base import BaseTestCase
from tests.test_utilities import test_login

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
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
SIM_RESULTS = _TEST_JSON['simulation_results']


class TestSaveSimulationService(BaseTestCase):
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

    def test_save_user_sim_empty_json(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/simulation',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_save_user_sim_invalid_json_no_configs(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/simulation',
                data=json.dumps({'alloy_store': ALLOY_STORE}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'Missing Configurations in payload.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_save_user_sim_invalid_json_no_alloy(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/simulation',
                data=json.dumps({'configurations': CONFIGS}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'Missing Alloy Store in payload.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_save_user_sim_invalid_missing_alloy(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            alloy_store = deepcopy(ALLOY_STORE)
            del alloy_store['alloys']['parent']['compositions'][-1]

            res = client.post(
                '/v1/sim/user/simulation',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': SIM_RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = "Missing elements ['Fe']"
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Missing element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_save_user_sim_invalid_bad_alloy(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'].append(
                {
                    'symbol': 'Vb',
                    'weight': 0.0
                }
            )

            res = client.post(
                '/v1/sim/user/simulation',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': SIM_RESULTS
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
            self.assertEqual(data['message'], 'Invalid element symbol error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_save_user_sim_success(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.post(
                '/v1/sim/user/simulation',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIM_RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['status'], 'success')
            self.assertTrue(data.get('data', None))
            self.assertEqual(res.status_code, 201)

            # Check it saved to the database and with the correct user
            _id = data['data']['_id']
            saved_inst = SavedSimulation.objects.get(id=_id)

            self.assertEqual(saved_inst.user.email, 'ironman@avengers.com')
            self.assertEqual(saved_inst.user.first_name, 'Tony')
            self.assertEqual(saved_inst.user.last_name, 'Stark')

            expected_alloy = deepcopy(ALLOY_STORE)
            alloy_id = data['data']['alloy_store']['alloys']['parent']['_id']
            expected_alloy['alloys']['parent']['_id'] = alloy_id

            self.assertDictEqual(saved_inst.configurations.to_dict(), CONFIGS)
            self.assertDictEqual(
                saved_inst.alloy_store.to_dict(), expected_alloy
            )

    def test_get_empty_sim_list(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.get(
                '/v1/sim/user/simulation', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No saved simulations found.')
            self.assert404(res)

    def test_get_saved_sim_list(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)
            configs2 = deepcopy(CONFIGS)
            alloy_store2 = deepcopy(ALLOY_STORE)
            configs2['method'] = 'Kirkaldy83'
            alloy_store2['alloys']['parent']['compositions'][0]['weight'] = 0.5

            saved_sim1 = SavedSimulation(
                **{
                    'user': self.tony,
                    'configurations': Configuration(**CONFIGS),
                    'alloy_store': AlloyStore(**ALLOY_STORE),
                    'simulation_results': SIM_RESULTS
                }
            ).save()
            saved_sim2 = SavedSimulation(
                **{
                    'user': self.tony,
                    'configurations': Configuration(**configs2),
                    'alloy_store': AlloyStore(**alloy_store2),
                    'simulation_results': SIM_RESULTS
                }
            ).save()

            res = client.get(
                '/v1/sim/user/simulation', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertTrue(data.get('data', False))
            self.assertDictEqual(
                saved_sim1.configurations.to_dict(),
                data['data'][0]['configurations']
            )
            self.assertDictEqual(
                saved_sim1.alloy_store.to_dict(),
                data['data'][0]['alloy_store']
            )
            self.assertDictEqual(
                saved_sim2.configurations.to_dict(),
                data['data'][1]['configurations']
            )
            self.assertDictEqual(
                saved_sim2.alloy_store.to_dict(),
                data['data'][1]['alloy_store']
            )

    def test_get_saved_sim_invalid_id(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.get(
                '/v1/sim/user/simulation/BadObjectId',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assert400(res)

    def test_get_saved_sim_empty(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)
            sim_id = ObjectId()

            res = client.get(
                f'/v1/sim/user/simulation/{sim_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Does not exist.')
            self.assert404(res)

    def test_get_saved_sim_detail_success(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)
            saved_sim = SavedSimulation(
                user=self.tony,
                configurations=Configuration(**CONFIGS),
                alloy_store=AlloyStore(**ALLOY_STORE),
                simulation_results=SIM_RESULTS
            ).save()

            res = client.get(
                f'/v1/sim/user/simulation/{saved_sim.id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data.get('data', False))
            self.assertDictEqual(
                saved_sim.configurations.to_dict(),
                data['data']['configurations']
            )
            self.assertDictEqual(
                saved_sim.alloy_store.to_dict(), data['data']['alloy_store']
            )
            self.assert200(res)

    def test_delete_saved_sim_invalid_id(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)

            res = client.delete(
                '/v1/sim/user/simulation/BadObjectId',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assert400(res)

    def test_delete_saved_sim_empty(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)
            sim_id = ObjectId()

            res = client.delete(
                f'/v1/sim/user/simulation/{sim_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Does not exist.')
            self.assert404(res)

    def test_delete_saved_sim_detail_success(self):
        with app.test_client() as client:
            cookie = test_login(client, self.tony.email, self._tony_pw)
            saved_sim = SavedSimulation(
                user=self.tony,
                configurations=Configuration(**CONFIGS),
                alloy_store=AlloyStore(**ALLOY_STORE),
                simulation_results=SIM_RESULTS
            ).save()

            res = client.delete(
                f'/v1/sim/user/simulation/{saved_sim.id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            with self.assertRaises(DoesNotExist):
                SavedSimulation.objects.get(id=saved_sim.id)


if __name__ == '__main__':
    unittest.main()
