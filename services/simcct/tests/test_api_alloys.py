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
import unittest
from pathlib import Path

from bson import ObjectId
from flask import current_app as app
from flask import json
from pymongo import MongoClient

from tests.test_api_base import BaseTestCase
from sim_app.app import BASE_DIR
from sim_app.mongo import MongoAlloys
from sim_app.schemas import AlloySchema

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'

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

    def test_get_all_alloys(self):
        """Ensure we can get all alloys."""
        # Clear the database so we can count properly.
        path = Path(BASE_DIR) / 'seed_alloy_data.json'
        with open(path) as f:
            json_data = json.load(f)

        conn = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
        db = conn['arc_dev']

        alloys_num = 0
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
            res = client.post(
                '/global/alloys',
                data=json.dumps(
                    {
                        'name': 'Alloy-1',
                        'compositions': test_json['compositions']
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 201)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])

    def test_create_alloy_empty_json(self):
        with app.test_client() as client:
            res = client.post(
                '/global/alloys',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_create_alloy_invalid_json(self):
        with app.test_client() as client:
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
            'Alloy-620',
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

    def test_update_by_id_single_alloy(self):
        """Ensure we can update an alloy."""
        with app.test_client() as client:
            alloy_data = {
                'name':
                'Alloy-600',
                'compositions': [
                    {
                        'symbol': 'C',
                        'weight': 1.0
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

            new_alloy_data = {
                'name':
                'Alloy-600',
                'compositions': [
                    {
                        'symbol': 'C',
                        'weight': 2.0
                    }, {
                        'symbol': 'Cr',
                        'weight': 3.0
                    }
                ]
            }

            _id = str(alloy_id)
            res = client.patch(
                f'/global/alloys/{_id}',
                data=json.dumps(new_alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            alloy_data['_id'] = data['data']['_id']
            alloy_data['compositions'][0] = {'symbol': 'C', 'weight': 2.0}
            alloy_data['compositions'].append({'symbol': 'Cr', 'weight': 3.0})
            self.assertEqual(data['data'], schema.dump(alloy_data))

    def test_update_single_alloy_by_addition(self):
        """Ensure we can partially just add a single element to an alloy."""
        with app.test_client() as client:
            alloy_data = {
                'name':
                'Alloy-500',
                'compositions': [
                    {
                        'symbol': 'C',
                        'weight': 1.0
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

            new_alloy_data = {
                'name': 'Alloy-500',
                'compositions': [{
                    'symbol': 'Cr',
                    'weight': 3.0
                }]
            }

            _id = str(alloy_id)
            res = client.patch(
                f'/global/alloys/{_id}',
                data=json.dumps(new_alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            alloy_data['_id'] = data['data']['_id']
            alloy_data['compositions'].append({'symbol': 'Cr', 'weight': 3.0})
            self.assertEqual(data['data'], schema.dump(alloy_data))

    def test_update_alloy_validation_error(self):
        with app.test_client() as client:
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
            self.assertEqual(
                data['message'], 'Request data failed schema validation.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 400)
            self.assertTrue(data['errors'])

    def test_update_alloy_non_existing(self):
        """Ensure if we try to update before creating it errors."""
        alloy_data = {
            'name':
            'Alloy-600',
            'compositions': [
                {
                    'symbol': 'C',
                    'weight': 1.2
                }, {
                    'symbol': 'Ar',
                    'weight': 1.0
                }, {
                    'symbol': 'Mn',
                    'weight': 1.0
                }
            ]
        }
        with app.test_client() as client:

            _id = str(ObjectId())
            res = client.patch(
                f'/global/alloys/{_id}',
                data=json.dumps(alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['status'], 'fail')

    def test_update_alloy_empty_json(self):
        with app.test_client() as client:
            _id = str(ObjectId())
            res = client.patch(
                f'/global/alloys/{_id}',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_delete_alloy(self):
        alloy_data = {
            'name':
            'Alloy-620',
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
            _id = str(alloy_id)
            res = client.delete(
                f'/global/alloys/{_id}', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 202)
            self.assertEqual(data['status'], 'success')

    def test_delete_alloy_non_existing(self):
        with app.test_client() as client:
            _id = str(ObjectId())
            res = client.delete(
                f'/global/alloys/{_id}', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(data['status'], 'fail')

    def test_invalid_request_object_id(self):
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

        with app.test_client() as client:
            _id = 123456789
            res = client.delete(
                f'/global/alloys/{_id}', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')

            res = client.patch(
                f'/global/alloys/{_id}',
                data=json.dumps(alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assertEqual(data['status'], 'fail')

            res = client.get(
                f'/global/alloys/{_id}', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')


if __name__ == '__main__':
    unittest.main()
