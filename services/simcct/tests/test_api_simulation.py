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
import requests
import unittest
from pathlib import Path

from bson import ObjectId
from flask import current_app as app
from flask import json
from pymongo import MongoClient

from tests.test_api_base import BaseTestCase
from sim_app.sim_session import SimSessionService
from sim_app.schemas import AlloySchema, ConfigurationsSchema, AlloyStoreSchema
from settings import BASE_DIR

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSimulationService(BaseTestCase):
    users_host = os.environ.get('USERS_HOST')
    base_url = f'http://{users_host}'
    _id = None

    @classmethod
    def setUpClass(cls) -> None:
        resp = requests.post(
            url=f'{cls.base_url}/auth/register',
            json={
                'email': 'jane@culver.edu.us',
                'first_name': 'Jane',
                'last_name': 'Foster',
                'password': 'IMissThor!!!'
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
        cls._id = data.get('data')['_id']

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete Jane so she's not registered again."""
        # We make a conn to Mongo
        mongo = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
        # user = mongo['arc_dev'].users.find_one({'_id': ObjectId(cls._id)})
        # print(user)
        # And just delete Jane from the db
        mongo.arc_dev.users.delete_one({'_id': ObjectId(cls._id)})

    def login_client(self, client):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = ConfigurationsSchema().load(test_json['configurations'])

        alloy = AlloySchema().load(
            {
                'name': 'Arc_Stark',
                'compositions': test_json['compositions']
            }
        )
        store = {
            'alloy_option': 'single',
            'alloys': {
                'parent': alloy,
                'weld': None,
                'mix': None
            }
        }
        alloy_store = AlloyStoreSchema().load(store)

        sess_res = client.post(
            '/session/login',
            data=json.dumps(
                {
                    '_id': self._id,
                    'is_admin': False,
                    'last_configurations': configs,
                    'last_alloy_store': alloy_store
                }
            ),
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='application/json'
        )
        data = json.loads(sess_res.data.decode())
        self.session_key = data['session_key']
        _, session_store = SimSessionService().load_session(self.session_key)
        session_alloy = session_store.get('alloy_store')
        self.assertEqual(data['status'], 'success')
        self.assertTrue(sess_res.status_code == 201)
        self.assertEqual(
            alloy_store['alloys']['parent'], session_alloy['alloys']['parent']
        )

    def test_simulate_no_prev_configs(self):
        """Ensure that if they have no previous configurations set it fails."""
        with app.test_client() as client:

            res = client.get(
                '/simulate',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': 'SessionKey!'
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'No previous session configurations was set.'
            )

    def test_simulate_no_prev_alloy(self):
        """Ensure that if the user does not have a previous alloy it fails."""
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)
        configs = ConfigurationsSchema().load(test_json['configurations'])
        with app.test_client() as client:
            sess_res = client.post(
                '/session/login',
                data=json.dumps(
                    {
                        '_id': self._id,
                        'is_admin': False,
                        'last_configurations': configs,
                        'last_alloy_store': {}
                    }
                ),
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='application/json'
            )
            data = json.loads(sess_res.data.decode())
            session_key = data['session_key']
            sid, session_store = SimSessionService().load_session(session_key)
            session_configs = session_store.get('configurations')
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_res.status_code == 201)
            self.assertEqual(configs, session_configs)

            res = client.get(
                '/simulate',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': session_key
                },
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
                '/configs/ae',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            self.assert200(res)

            res = client.get(
                '/configs/ms',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            self.assert200(res)
            res = client.get(
                '/configs/bs',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            self.assert200(res)

            # Now we can run
            res = client.get(
                '/simulate',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
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
