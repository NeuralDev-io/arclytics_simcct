# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.14'
"""test_api_alloys.py: 

Test all the endpoints on the Alloy resources endpoint.
"""

import os
import requests
import unittest
from pathlib import Path

from bson import ObjectId
from flask import current_app as app
from flask import json
from pymongo import MongoClient

import settings
from tests.test_api_base import BaseTestCase
from sim_app.mongo import MongoAlloys
from sim_app.sim_session import SimSessionService
from sim_app.schemas import AlloySchema, ConfigurationsSchema, AlloyStoreSchema

_TEST_CONFIGS_PATH = Path(
    settings.BASE_DIR
) / 'simulation' / 'sim_configs.json'

schema = AlloySchema()


class TestAlloyService(BaseTestCase):
    alloy_data = {
        'name':
        'Alloy-101',
        'compositions': [
            {
                'symbol': 'C',
                'weight': 2.0
            }, {
                'symbol': 'Ar',
                'weight': 1.0
            }, {
                'symbol': 'Mn',
                'weight': 1.0
            }
        ]
    }

    users_host = os.environ.get('USERS_HOST')
    base_url = f'http://{users_host}'
    _id = None
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.mongo = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )

        resp = requests.post(
            url=f'{cls.base_url}/auth/register',
            json={
                'email': 'shuri@wakanda.com',
                'first_name': 'Shuri',
                'last_name': 'Wakandan',
                'password': 'WhatAreTHOOOOSSSEEE!!!!!',
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
        # We just delete Shuri from the db
        cls.mongo.arc_dev.users.delete_one({'_id': ObjectId(cls._id)})

    def login_client(self, client):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = ConfigurationsSchema().load(test_json['configurations'])

        alloy = AlloySchema().load(
            {
                'name': 'Vibranium',
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
                    'is_admin': True,
                    'last_configurations': configs,
                    'last_alloy_store': alloy_store
                }
            ),
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='application/json'
        )
        data = json.loads(sess_res.data.decode())
        self.session_key = data['session_key']

    def test_get_all_alloys(self):
        """Ensure we can get all alloys."""
        # Clear the database so we can count properly.
        path = Path(settings.BASE_DIR) / 'seed_alloy_data.json'
        with open(path) as f:
            json_data = json.load(f)

        conn = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
        db = conn['arc_dev']

        if len([alloy for alloy in db.alloys.find()]) == 0:
            data = AlloySchema(many=True).load(json_data['alloys'])
            created_id_list = MongoAlloys().create_many(data)
            alloys_num = len(created_id_list)
        else:
            alloys_num = len([alloy for alloy in db.alloys.find()])

        with app.test_client() as client:
            res = client.get('/global/alloys', content_type='application/json')
            data = json.loads(res.data.decode())

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['alloys'])
            self.assertEqual(len(data['alloys']), alloys_num)

    # def test_get_alloy_list_empty(self):
    #     # Clear the database so we can count properly.
    #     with app.test_client() as client:
    #         res = client.get('/global/alloys',
    #         content_type='application/json')
    #         data = json.loads(res.data.decode())
    #
    #         self.assertEqual(res.status_code, 404)
    #         self.assertEqual(data['status'], 'fail')
    #         with self.assertRaises(KeyError):
    #             self.assertTrue(data['alloys'])

    def test_create_alloy(self):
        """Ensure we can create an alloy."""
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        # POST method requires a list, not a dict like the others.
        with app.test_client() as client:
            self.login_client(client)
            res = client.post(
                '/global/alloys',
                data=json.dumps(
                    {
                        'name': 'Alloy-1',
                        'compositions': test_json['compositions']
                    }
                ),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            self.assertTrue(data['data'])

    def test_create_alloy_no_session_key(self):
        with app.test_client() as client:
            res = client.post(
                '/global/alloys',
                data=json.dumps({}),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': ''
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'No Session key in header.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 401)

    def test_create_alloy_no_token(self):
        with app.test_client() as client:
            res = client.post(
                '/global/alloys',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'No valid Authorization in header.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 401)

    def test_create_alloy_empty_json(self):
        with app.test_client() as client:
            self.login_client(client)
            res = client.post(
                '/global/alloys',
                data=json.dumps({}),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_create_alloy_invalid_json(self):
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/global/alloys',
                data=json.dumps(
                    {
                        'name': 'Alloy-1',
                        'compositions': [{
                            'name': 'carbon',
                            'weight': 0.1
                        }]
                    }
                ),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertTrue(data['errors'])
            err = {
                'compositions': {
                    '0': {
                        'symbol': ['Missing data for required field.']
                    }
                }
            }
            self.assertEqual(data['errors'], err)

    def test_create_duplicate_name_alloy(self):
        """Ensure we can't create a duplicate alloy."""
        with app.test_client() as client:
            self.login_client(client)

            alloy_data = {
                'name':
                'Alloy-666',
                'compositions': [
                    {
                        'symbol': 'C',
                        'weight': 2.0
                    }, {
                        'symbol': 'Ar',
                        'weight': 1.0
                    }, {
                        'symbol': 'Mn',
                        'weight': 1.0
                    }
                ]
            }

            data = AlloySchema().load(alloy_data)
            alloy_id = MongoAlloys().create(data)
            self.assertIsInstance(alloy_id, ObjectId)

            duplicate_alloy = {
                'name':
                'Alloy-666',
                'compositions': [
                    {
                        'symbol': 'C',
                        'weight': 2.0
                    }, {
                        'symbol': 'Mn',
                        'weight': 1.0
                    }
                ]
            }

            _id = str(alloy_id)
            res = client.post(
                '/global/alloys',
                data=json.dumps(duplicate_alloy),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 412)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Alloy already exists.')

    def test_get_single_alloy(self):
        """Ensure we can retrieve a single alloy."""
        alloy_data = {
            'name':
            'Alloy-660',
            'compositions': [
                {
                    'symbol': 'C',
                    'weight': 2.0
                }, {
                    'symbol': 'Ar',
                    'weight': 1.0
                }, {
                    'symbol': 'Mn',
                    'weight': 1.0
                }
            ]
        }

        data = schema.load(alloy_data)
        alloy_id = MongoAlloys().create(data)
        self.assertIsInstance(alloy_id, ObjectId)

        with app.test_client() as client:
            res = client.get(
                f'/global/alloys/{alloy_id}', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            _alloy = alloy_data
            _alloy['_id'] = data['data']['_id']
            self.assertEqual(data['data'], schema.dump(_alloy))

    def test_get_single_alloy_non_existing(self):
        with app.test_client() as client:
            _id = str(ObjectId())
            res = client.get(
                f'/global/alloys/{_id}', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(data['status'], 'fail')

    def test_update_alloy_using_invalid_patch(self):
        with app.test_client() as client:
            self.login_client(client)

            bad_alloy_data = {
                'name':
                'Alloy-626',
                'compositions': [
                    {
                        'symbol': 'C'
                    }, {
                        'symbol': 'Ar'
                    }, {
                        'symbol': 'Mn',
                        'weight': 1.0
                    }
                ]
            }

            _id = str(ObjectId())
            res = client.patch(
                f'/global/alloys/{_id}',
                data=json.dumps(bad_alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = (
                'Method Not Allowed. These are not the endpoints you are '
                'looking for.'
            )
            self.assertEqual(data['message'], msg)
            self.assertEqual(res.status_code, 405)

    def test_update_by_id_single_alloy(self):
        """Ensure we can update an alloy."""
        with app.test_client() as client:
            self.login_client(client)

            alloy_data = {
                'name':
                'Alloy-600',
                'compositions': [
                    {
                        "symbol": "C",
                        "weight": 0.044
                    }, {
                        "symbol": "Mn",
                        "weight": 1.73
                    }, {
                        "symbol": "Si",
                        "weight": 0.22
                    }, {
                        "symbol": "Ni",
                        "weight": 0.0
                    }, {
                        "symbol": "Cr",
                        "weight": 0.0
                    }, {
                        "symbol": "Mo",
                        "weight": 0.26
                    }, {
                        "symbol": "Co",
                        "weight": 0.0
                    }, {
                        "symbol": "Al",
                        "weight": 0.0
                    }, {
                        "symbol": "Cu",
                        "weight": 0.0
                    }, {
                        "symbol": "As",
                        "weight": 0.0
                    }, {
                        "symbol": "Ti",
                        "weight": 0.0
                    }, {
                        "symbol": "V",
                        "weight": 0.0
                    }, {
                        "symbol": "W",
                        "weight": 0.0
                    }, {
                        "symbol": "S",
                        "weight": 0.0
                    }, {
                        "symbol": "N",
                        "weight": 0.0
                    }, {
                        "symbol": "Nb",
                        "weight": 0.0
                    }, {
                        "symbol": "B",
                        "weight": 0.0
                    }, {
                        "symbol": "P",
                        "weight": 0.0
                    }, {
                        "symbol": "Fe",
                        "weight": 0.0
                    }
                ]
            }

            data = schema.load(alloy_data)
            alloy_id = MongoAlloys().create(data)
            self.assertIsInstance(alloy_id, ObjectId)

            new_alloy_data = {
                'name':
                'Alloy-600',
                'compositions': [
                    {
                        "symbol": "C",
                        "weight": 0.5
                    }, {
                        "symbol": "Mn",
                        "weight": 1.73
                    }, {
                        "symbol": "Si",
                        "weight": 0.22
                    }, {
                        "symbol": "Ni",
                        "weight": 0.0
                    }, {
                        "symbol": "Cr",
                        "weight": 0.0
                    }, {
                        "symbol": "Mo",
                        "weight": 0.26
                    }, {
                        "symbol": "Co",
                        "weight": 0.0
                    }, {
                        "symbol": "Cu",
                        "weight": 0.0
                    }, {
                        "symbol": "As",
                        "weight": 0.0
                    }, {
                        "symbol": "Ti",
                        "weight": 0.0
                    }, {
                        "symbol": "W",
                        "weight": 0.0
                    }, {
                        "symbol": "S",
                        "weight": 0.0
                    }, {
                        "symbol": "N",
                        "weight": 0.0
                    }, {
                        "symbol": "Nb",
                        "weight": 0.0
                    }, {
                        "symbol": "B",
                        "weight": 0.0
                    }, {
                        "symbol": "P",
                        "weight": 0.0
                    }, {
                        "symbol": "Fe",
                        "weight": 0.0
                    }
                ]
            }

            _id = str(alloy_id)
            res = client.put(
                f'/global/alloys/{_id}',
                data=json.dumps(new_alloy_data),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            new_alloy_data['_id'] = data['data']['_id']
            self.assertDictEqual(data['data'], new_alloy_data)

    def test_update_alloy_validation_error(self):
        with app.test_client() as client:
            self.login_client(client)

            bad_alloy_data = {
                'name':
                'Alloy-626',
                'compositions': [
                    {
                        'symbol': 'C'
                    }, {
                        'symbol': 'Ar'
                    }, {
                        'symbol': 'Mn',
                        'weight': 1.0
                    }
                ]
            }

            _id = str(ObjectId())
            res = client.put(
                f'/global/alloys/{_id}',
                data=json.dumps(bad_alloy_data),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Request data failed schema validation.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 400)
            self.assertTrue(data['errors'])

    def test_update_alloy_non_existing(self):
        """Ensure if we try to update before creating it errors."""
        alloy_data = {
            'name': 'Alloy-600',
            'compositions': [{
                'symbol': 'C',
                'weight': 1.2
            }]
        }
        with app.test_client() as client:
            self.login_client(client)

            _id = str(ObjectId())
            res = client.put(
                f'/global/alloys/{_id}',
                data=json.dumps(alloy_data),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['status'], 'fail')

    def test_update_alloy_empty_json(self):
        with app.test_client() as client:
            self.login_client(client)
            _id = str(ObjectId())
            res = client.put(
                f'/global/alloys/{_id}',
                data=json.dumps({}),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 400)

    def test_delete_alloy(self):
        alloy_data = {
            'name':
            'Alloy-66',
            'compositions': [
                {
                    "symbol": "C",
                    "weight": 0.044
                }, {
                    "symbol": "Mn",
                    "weight": 1.73
                }, {
                    "symbol": "Si",
                    "weight": 0.22
                }, {
                    "symbol": "Ni",
                    "weight": 0.0
                }, {
                    "symbol": "Cr",
                    "weight": 0.0
                }, {
                    "symbol": "Mo",
                    "weight": 0.26
                }, {
                    "symbol": "Co",
                    "weight": 0.0
                }, {
                    "symbol": "Cu",
                    "weight": 0.0
                }, {
                    "symbol": "As",
                    "weight": 0.0
                }, {
                    "symbol": "Ti",
                    "weight": 0.0
                }, {
                    "symbol": "W",
                    "weight": 0.0
                }, {
                    "symbol": "Fe",
                    "weight": 0.0
                }
            ]
        }

        data = schema.load(alloy_data)
        alloy_id = MongoAlloys().create(data)
        self.assertIsInstance(alloy_id, ObjectId)

        with app.test_client() as client:
            self.login_client(client)
            _id = str(alloy_id)

            res = client.delete(
                f'/global/alloys/{_id}',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 202)
            self.assertEqual(data['status'], 'success')

    def test_delete_alloy_non_existing(self):
        with app.test_client() as client:
            self.login_client(client)
            _id = str(ObjectId())

            res = client.delete(
                f'/global/alloys/{_id}',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(data['status'], 'fail')

    def test_invalid_request_object_id(self):
        """Ensure if we send an invalid ObjectId to the ones that require them
        we get an error.
        """
        alloy_data = {
            'name': 'Alloy-101',
            'compositions': [{
                'symbol': 'C',
                'weight': 2.0
            }]
        }

        with app.test_client() as client:
            self.login_client(client)
            _id = 123456789

            res = client.delete(
                f'/global/alloys/{_id}',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')

            res = client.put(
                f'/global/alloys/{_id}',
                data=json.dumps(alloy_data),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assertEqual(data['status'], 'fail')

            res = client.get(
                f'/global/alloys/{_id}',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Session': self.session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')


if __name__ == '__main__':
    unittest.main()
