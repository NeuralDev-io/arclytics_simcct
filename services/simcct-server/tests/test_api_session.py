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
        with self.client:
            res = self.client.get('/users/ping')
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['message'], 'pong')
            self.assertEqual(data['status'], 'success')

    def test_session_post(self):
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
                data=json.dumps({
                    '_id': user_id,
                    'token': token,
                    'last_configurations': test_json['configurations']
                }),
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')

    def test_login_user_with_no_configurations(self):
        """
        Ensure that if the user logged in without configurations it defaults to
        the empty configs.
        """
        _id = ObjectId()
        with current_app.test_client() as client:
            login_res = client.post(
                '/session',
                data=json.dumps({
                    '_id': str(_id),
                    'token': "ThisIsOnlyATestingToken",
                    'last_configurations': {}
                }),
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            sess_saved = session.get(f'{str(_id)}:last_configurations')
            self.assertEqual(sess_saved['method'], 'Li98')

    def test_login_user_with_configurations(self):
        """
        Ensure that if a user has an appropriate last_configurations then
        it is set appropriately.
        """
        pass

    def test_login_user_with_compositions(self):
        """Ensure if the user a last_compositions it is added to Redis store."""
        _id = ObjectId()
        e1 = {'name': 'carbon', 'symbol': 'cx', 'weight': 0.044}
        e2 = {'name': 'manganese', 'symbol': 'mn', 'weight': 1.73}
        e3 = {'name': 'silicon', 'symbol': 'si', 'weight': 0.22}

        with current_app.test_client() as client:
            login_res = client.post(
                '/session',
                data=json.dumps({
                    '_id': str(_id),
                    'token': "ThisIsOnlyATestingToken",
                    'last_configurations': {},
                    'last_compositions': {'comp': [e1, e2, e3]}
                }),
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')
            comp_store = session.get(f'{str(_id)}:last_compositions')
            self.assertTrue(comp_store['comp'])
            self.assertEqual(comp_store['comp'][0]['name'], e1['name'])
            self.assertEqual(comp_store['comp'][0]['symbol'], e1['symbol'])
            self.assertEqual(comp_store['comp'][0]['weight'], e1['weight'])
            self.assertEqual(comp_store['comp'][1]['name'], e1['name'])
            self.assertEqual(comp_store['comp'][1]['symbol'], e1['symbol'])
            self.assertEqual(comp_store['comp'][1]['weight'], e1['weight'])
            self.assertEqual(comp_store['comp'][2]['name'], e1['name'])
            self.assertEqual(comp_store['comp'][2]['symbol'], e1['symbol'])
            self.assertEqual(comp_store['comp'][2]['weight'], e1['weight'])
