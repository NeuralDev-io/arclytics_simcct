# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.13'

import unittest
from copy import deepcopy
from pathlib import Path

from bson import ObjectId
from flask import json
from flask import current_app as app
from mongoengine import DoesNotExist

import settings
from tests.test_api_base import BaseTestCase
from arc_app.models import User, Configuration, AlloyStore, SavedSimulation

_TEST_CONFIGS_PATH = Path(settings.BASE_DIR) / 'tests' / 'sim_configs.json'
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


class TestSaveSimulationService(BaseTestCase):
    user = None

    def setUp(self) -> None:
        self.user = User(
            first_name='Scott', last_name='Lang', email='ant-man@marvel.com'
        )
        self.user.set_password('TimeVortex!')
        self.user.verified = True
        self.user.save()

    def tearDown(self) -> None:
        self.user.delete()

    @staticmethod
    def login(client, email='ant-man@marvel.com', password='TimeVortex!'):
        resp_login = client.post(
            '/auth/login',
            data=json.dumps({
                'email': email,
                'password': password
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['token']
        return token

    def test_save_user_sim_empty_json(self):
        with app.test_client() as client:
            token = self.login(client)

            res = client.post(
                '/user/simulation',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_save_user_sim_invalid_json_no_configs(self):
        with app.test_client() as client:
            token = self.login(client)

            res = client.post(
                '/user/simulation',
                data=json.dumps({'alloy_store': ALLOY_STORE}),
                headers={'Authorization': f'Bearer {token}'},
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
            token = self.login(client)

            res = client.post(
                '/user/simulation',
                data=json.dumps({'configurations': CONFIGS}),
                headers={'Authorization': f'Bearer {token}'},
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
            token = self.login(client)

            alloy_store = deepcopy(ALLOY_STORE)
            del alloy_store['alloys']['parent']['compositions'][-1]

            res = client.post(
                '/user/simulation',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
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
            token = self.login(client)

            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'].append(
                {
                    'symbol': 'Vb',
                    'weight': 0.0
                }
            )

            res = client.post(
                '/user/simulation',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
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
            token = self.login(client)

            res = client.post(
                '/user/simulation',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['status'], 'success')
            self.assertTrue(data.get('data', None))
            self.assertEqual(res.status_code, 201)

            # Check it saved to the database and with the correct user
            _id = data['data']['_id']
            saved_inst = SavedSimulation.objects.get(id=_id)

            self.assertEqual(saved_inst.user.email, 'ant-man@marvel.com')
            self.assertEqual(saved_inst.user.first_name, 'Scott')
            self.assertEqual(saved_inst.user.last_name, 'Lang')

            expected_alloy = deepcopy(ALLOY_STORE)
            alloy_id = data['data']['alloy_store']['alloys']['parent']['_id']
            expected_alloy['alloys']['parent']['_id'] = alloy_id

            self.assertDictEqual(saved_inst.configurations.to_dict(), CONFIGS)
            self.assertDictEqual(
                saved_inst.alloy_store.to_dict(), expected_alloy
            )

    def test_get_empty_sim_list(self):
        with app.test_client() as client:
            token = self.login(client)

            res = client.get(
                '/user/simulation',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No saved simulations found.')
            self.assert404(res)

    def test_get_saved_sim_list(self):
        with app.test_client() as client:
            token = self.login(client)
            configs2 = deepcopy(CONFIGS)
            alloy_store2 = deepcopy(ALLOY_STORE)
            configs2['method'] = 'Kirkaldy83'
            alloy_store2['alloys']['parent']['compositions'][0]['weight'] = 0.5

            saved_sim1 = SavedSimulation(
                **{
                    'user': self.user,
                    'configurations': Configuration(**CONFIGS),
                    'alloy_store': AlloyStore(**ALLOY_STORE)
                }
            ).save()
            saved_sim2 = SavedSimulation(
                **{
                    'user': self.user,
                    'configurations': Configuration(**configs2),
                    'alloy_store': AlloyStore(**alloy_store2)
                }
            ).save()

            res = client.get(
                '/user/simulation',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
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
            token = self.login(client)

            res = client.get(
                '/user/simulation/BadObjectId',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assert400(res)

    def test_get_saved_sim_empty(self):
        with app.test_client() as client:
            token = self.login(client)
            sim_id = ObjectId()

            res = client.get(
                f'/user/simulation/{sim_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Does not exist.')
            self.assert404(res)

    def test_get_saved_sim_detail_success(self):
        with app.test_client() as client:
            token = self.login(client)
            saved_sim = SavedSimulation(
                user=self.user,
                configurations=Configuration(**CONFIGS),
                alloy_store=AlloyStore(**ALLOY_STORE)
            ).save()

            res = client.get(
                f'/user/simulation/{saved_sim.id}',
                headers={'Authorization': f'Bearer {token}'},
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
            token = self.login(client)

            res = client.delete(
                '/user/simulation/BadObjectId',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assert400(res)

    def test_delete_saved_sim_empty(self):
        with app.test_client() as client:
            token = self.login(client)
            sim_id = ObjectId()

            res = client.delete(
                f'/user/simulation/{sim_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Does not exist.')
            self.assert404(res)

    def test_delete_saved_sim_detail_success(self):
        with app.test_client() as client:
            token = self.login(client)
            saved_sim = SavedSimulation(
                user=self.user,
                configurations=Configuration(**CONFIGS),
                alloy_store=AlloyStore(**ALLOY_STORE)
            ).save()

            res = client.delete(
                f'/user/simulation/{saved_sim.id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            with self.assertRaises(DoesNotExist):
                SavedSimulation.objects.get(id=saved_sim.id)


if __name__ == '__main__':
    unittest.main()
