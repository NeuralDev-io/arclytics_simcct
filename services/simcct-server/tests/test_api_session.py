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

import os
import json
import requests
from pathlib import Path

from bson import ObjectId
from flask import current_app, session

from sim_api import BASE_DIR
from tests.test_api_base import BaseTestCase, app

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSessionService(BaseTestCase):
    users_host = os.environ.get('USERS_HOST')
    base_url = f'http://{users_host}'

    def test_session_user_ping(self):
        """Just a sanity check test that there is connection to users-server."""
        with self.client:
            res = self.client.get('/users/ping')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['message'], 'pong')
            self.assertEqual(data['status'], 'success')

    def test_session_post(self):
        """Ensure we can use the requests library to make registration/login
        to the users-server and get the correct responses.
        """
        resp = requests.post(
            url=f'{self.base_url}/auth/register',
            json={
                'email': 'eric@shield.gov.us',
                'first_name': 'Eric',
                'last_name': 'Selvig',
                'password': 'BifrostIsReal'
            }
        )
        data = resp.json()
        token = data['token']
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'User has been registered.')
        self.assertTrue(token)

        user_resp = requests.get(
            f'{self.base_url}/auth/status',
            headers={
                'Content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        data = user_resp.json()
        self.assertEqual(data['status'], 'success')
        user_id = data['data']['_id']

        with self.app.test_client() as client:
            with open(_TEST_CONFIGS_PATH, 'r') as f:
                test_json = json.load(f)

            login_res = client.post(
                '/session',
                data=json.dumps(
                    {
                        '_id': user_id,
                        'last_configurations': test_json['configurations']
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')

    def test_login_session_empty_post_data(self):
        with self.app.test_client() as client:

            login_res = client.post(
                '/session',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer JustATest!'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assert400(login_res)

    def test_login_session_no_user_id(self):
        with self.app.test_client() as client:
            token = 'TESTTESTTEST!'
            login_res = client.post(
                '/session',
                data=json.dumps({'token': 'ThisWontBeRead'}),
                headers={'Authorization': f'Bearer {token}'},
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
                '/session',
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
            _id = ObjectId()
            login_res = client.post(
                '/session',
                data=json.dumps({'_id': str(_id)}),
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
                '/session',
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

    def test_login_user_with_configurations(self):
        """Ensure that if a user has an appropriate last_configurations then
        it is set appropriately.
        """
        _id = ObjectId()

        configs = {
            'method': 'Li98',
            'alloy': 'parent',
            'grain_size': 8.0,
            'grain_size_type': 'ASTM',
            'nucleation_start': 1.0,
            'nucleation_finish': 99.9,
            'auto_calculate_xfe': True,
            'xfe_value': 0.0,
            'cf_value': 0.012,
            'ceut_value': 0.762,
            'auto_calculate_ms_bs': True,
            'transformation_method': 'Li98',
            'ms_temp': 0.0,
            'ms_undercool': 100.0,
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
                '/session',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'last_configurations': configs,
                        'last_compositions': {
                            'comp': []
                        }
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            sess_saved = session.get(f'{str(token)}:configurations')
            self.assertEqual(sess_saved['method'], 'Li98')
            self.assertEqual(sess_saved['alloy'], 'parent')
            self.assertEqual(sess_saved['grain_size_type'], 'ASTM')
            self.assertEqual(sess_saved['grain_size'], 8.0)
            self.assertEqual(sess_saved['auto_calculate_ms_bs'], True)

    def test_login_user_with_compositions(self):
        """Ensure if the user a last_compositions it is added to Redis store."""
        _id = ObjectId()
        e1 = {'name': 'carbon', 'symbol': 'cx', 'weight': 0.044}
        e2 = {'name': 'manganese', 'symbol': 'mn', 'weight': 1.73}
        e3 = {'name': 'silicon', 'symbol': 'si', 'weight': 0.22}
        token = 'ThisIsOnlyATestingToken'

        with current_app.test_client() as client:
            login_res = client.post(
                '/session',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'token': token,
                        'last_configurations': {},
                        'last_compositions': {
                            'comp': [e1, e2, e3]
                        }
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            comp_store = session.get(f'{str(token)}:compositions')
            self.assertTrue(comp_store['comp'])
            self.assertEqual(comp_store['comp'][0]['name'], e1['name'])
            self.assertEqual(comp_store['comp'][0]['symbol'], e1['symbol'])
            self.assertEqual(comp_store['comp'][0]['weight'], e1['weight'])
            self.assertEqual(comp_store['comp'][1]['name'], e2['name'])
            self.assertEqual(comp_store['comp'][1]['symbol'], e2['symbol'])
            self.assertEqual(comp_store['comp'][1]['weight'], e2['weight'])
            self.assertEqual(comp_store['comp'][2]['name'], e3['name'])
            self.assertEqual(comp_store['comp'][2]['symbol'], e3['symbol'])
            self.assertEqual(comp_store['comp'][2]['weight'], e3['weight'])
