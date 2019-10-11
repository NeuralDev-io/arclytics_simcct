# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_global_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.07.14'

import unittest
from pathlib import Path

from bson import ObjectId
from flask import json
from mongoengine import get_db

from manage import BASE_DIR
from sim_api.extensions import MongoAlloys
from sim_api.models import User, Configuration, AlloyStore, AdminProfile
from sim_api.schemas import AlloySchema, ConfigurationsSchema, AlloyStoreSchema
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login
from arc_logging import AppLogger

logger = AppLogger(__name__)

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'tests' / 'sim_configs.json'

with open(_TEST_CONFIGS_PATH, 'r') as f:
    test_json = json.load(f)

schema = AlloySchema()


class TestAlloyService(BaseTestCase):
    alloy_data = {
        'name':
        'Alloy-101',
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
    _email = None
    _shuri_pw = 'WhatAreTHOOOOSSSEEE!!!!!'
    _okoye_pw = 'WhyWasSheUpThereAllThisTime!?!'
    _id = None
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        assert app.config['TESTING'] is True
        cls.mongo = get_db('default')

        # SHURI is a NORMAL USER
        cls.shuri = User(
            **{
                'email': 'shuri@wakanda.com',
                'first_name': 'Shuri',
                'last_name': 'Wakandan',
            }
        )
        cls.shuri.set_password(cls._shuri_pw)

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

        cls.shuri.last_alloy_store = alloy_store
        cls.shuri.last_configuration = configs

        cls.shuri.save()

        # OKOYE is an ADMIN because she is boss
        cls.okoye = User(
            **{
                'email': 'okoye@wakanda.com',
                'first_name': 'Okoye',
                'last_name': 'Dora Milaje',
            }
        )

        cls.okoye.admin_profile = AdminProfile(
            **{
                'position': 'General',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        cls.okoye.disable_admin = False
        cls.okoye.set_password(cls._okoye_pw)
        cls.okoye.save()

        user_shuri = cls.mongo.users.find_one({'email': 'shuri@wakanda.com'})
        user_okoye = cls.mongo.users.find_one({'email': 'okoye@wakanda.com'})
        assert user_shuri is not None
        assert user_okoye is not None
        assert user_okoye['admin'] is True

        cls._id = cls.shuri.id
        cls._email = cls.shuri.email

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete Shuri so no conflict."""
        # We just delete Shuri from the db
        db = get_db('default')
        db.users.drop()

    def test_get_all_alloys(self):
        """Ensure we can get all alloys."""
        # Clear the database so we can count properly.
        path = Path(BASE_DIR) / 'seed_alloy_data.json'
        with open(path) as f:
            json_data = json.load(f)

        db = get_db()
        self.assertEqual(db.name, 'arc_test')
        if len([alloy for alloy in db.alloys.find()]) == 0:
            data = AlloySchema(many=True).load(json_data['alloys'])
            created_id_list = MongoAlloys().create_many(data)
            alloys_num = len(created_id_list)
        else:
            alloys_num = len([alloy for alloy in db.alloys.find()])

        with self.client as client:
            test_login(client, self.shuri.email, self._shuri_pw)

            res = client.get(
                '/v1/sim/global/alloys', content_type='application/json'
            )
            data = res.json

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            self.assertEqual(len(data['data']), alloys_num)

    def test_get_alloy_list_empty(self):
        # Clear the database so we can count properly.
        # Drop the collection with the current database (should be arc_test)
        db = get_db()
        self.assertEqual(db.name, 'arc_test')
        db.alloys.drop()

        with self.app.test_client() as client:
            test_login(client, self.shuri.email, self._shuri_pw)

            res = client.get(
                '/v1/sim/global/alloys', content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['status'], 'fail')
            with self.assertRaises(KeyError):
                self.assertTrue(data['alloys'])

    def test_create_alloy(self):
        """Ensure we can create an alloy."""

        # POST method requires a list, not a dict like the others.
        with self.app.test_client() as client:
            # We need to make an admin user
            test_login(client, self.okoye.email, self._okoye_pw)

            res = client.post(
                '/v1/sim/global/alloys',
                data=json.dumps(
                    {
                        'name': 'Alloy-1',
                        'compositions': test_json['compositions']
                    }
                ),
                content_type='application/json'
            )
            data = res.json
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            self.assertTrue(data['data'])

    def test_create_alloy_not_authorized(self):
        with self.app.test_client() as client:
            # Shuri is not an admin so can't create
            test_login(client, self.shuri.email, self._shuri_pw)

            res = client.post(
                '/v1/sim/global/alloys',
                data=json.dumps({}),  # Middleware before View method
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Not authorized.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 403)

    def test_create_alloy_no_cookie(self):
        with self.app.test_client() as client:
            # If we don't login, we have no cookie
            # We also assert there is no cookie with the current client
            # The cookie_jar is a MultiDict
            self.assertEqual(len(client.cookie_jar), 0)

            res = client.post(
                '/v1/sim/global/alloys',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 401)

    def test_create_alloy_no_session(self):
        with self.client as client:
            # If we don't login, we have no cookie
            # We also assert there is no cookie with the current client
            # The cookie_jar is a MultiDict
            test_login(client, self.shuri.email, self._shuri_pw)

            # Save the cookie from login
            cookie = next(
                (
                    cookie for cookie in client.cookie_jar
                    if cookie.name == 'SESSION_TOKEN'
                ), None
            )

            # Logging out should clear the session
            client.get('/v1/sim/auth/logout', content_type='application/json')

            # Clear the cookie from previously although it should be
            # cleared by logout
            # client.cookie_jar.clear()
            self.assertEqual(len(client.cookie_jar), 0)

            # We set the old Cookie back and see if it works
            client.set_cookie('localhost', 'SESSION_TOKEN', cookie.value)

            res = client.post(
                '/v1/sim/global/alloys',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Session is invalid.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 401)

    def test_create_alloy_empty_json(self):
        with self.client as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            res = client.post(
                '/v1/sim/global/alloys',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = res.json

            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_create_alloy_invalid_json(self):
        with self.client as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            res = client.post(
                '/v1/sim/global/alloys',
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
            data = res.json

            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid element error.')
            self.assertTrue(data['error'])
            err = (
                'ValidationError (Element) (Field is required: '
                '["Element.symbol"].)'
            )
            self.assertEqual(data['error'], err)

    def test_create_duplicate_name_alloy(self):
        """Ensure we can't create a duplicate alloy."""
        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            alloy_data = self.alloy_data.copy()
            alloy_data['name'] = 'Duplicate'

            data = AlloySchema().load(alloy_data)
            alloy_id = MongoAlloys().create(data)
            self.assertIsInstance(alloy_id, ObjectId)

            duplicate_alloy = self.alloy_data.copy()
            duplicate_alloy['name'] = 'Duplicate'

            _id = str(alloy_id)
            res = client.post(
                '/v1/sim/global/alloys',
                data=json.dumps(duplicate_alloy),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 412)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Alloy already exists.')

    def test_get_single_alloy(self):
        """Ensure we can retrieve a single alloy."""
        alloy_data = self.alloy_data.copy()
        alloy_data['name'] = 'Alloy-Get-1'

        data = schema.load(alloy_data)
        alloy_id = MongoAlloys().create(data)
        self.assertIsInstance(alloy_id, ObjectId)

        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            res = client.get(
                f'/v1/sim/global/alloys/{alloy_id}',
                content_type='application/json'
            )
            data = res.json
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            _alloy = alloy_data
            _alloy['_id'] = data['data']['_id']
            self.assertEqual(data['data'], schema.dump(_alloy))

    def test_get_single_alloy_non_existing(self):
        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            _id = str(ObjectId())
            res = client.get(
                f'/v1/sim/global/alloys/{_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(data['status'], 'fail')

    def test_update_alloy_using_invalid_patch(self):
        with app.test_client() as client:
            test_login(client, self.shuri.email, self._shuri_pw)

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
                f'/v1/sim/global/alloys/{_id}',
                data=json.dumps(bad_alloy_data),
                content_type='application/json'
            )
            data = res.json
            msg = (
                'Method Not Allowed. These are not the endpoints you are '
                'looking for.'
            )
            self.assertEqual(data['message'], msg)
            self.assertEqual(res.status_code, 405)

    def test_update_by_id_single_alloy(self):
        """Ensure we can update an alloy."""
        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

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
                f'/v1/sim/global/alloys/{_id}',
                data=json.dumps(new_alloy_data),
                content_type='application/json'
            )
            data = res.json
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            new_alloy_data['_id'] = data['data']['_id']
            self.assertDictEqual(data['data'], new_alloy_data)

    def test_update_alloy_validation_error(self):
        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

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
                f'/v1/sim/global/alloys/{_id}',
                data=json.dumps(bad_alloy_data),
                content_type='application/json'
            )
            data = res.json
            self.assertEqual(data['message'], 'Missing element error.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 400)
            self.assertTrue(data['error'])

    def test_update_alloy_non_existing(self):
        """Ensure if we try to update before creating it errors."""
        alloy_data = self.alloy_data.copy()
        alloy_data['name'] = 'Alloy Before Login'

        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            _id = str(ObjectId())
            res = client.put(
                f'/v1/sim/global/alloys/{_id}',
                data=json.dumps(alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['status'], 'fail')

    def test_update_alloy_empty_json(self):
        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            _id = str(ObjectId())
            res = client.put(
                f'/v1/sim/global/alloys/{_id}',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = res.json
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
            test_login(client, self.okoye.email, self._okoye_pw)

            _id = str(alloy_id)

            res = client.delete(
                f'/v1/sim/global/alloys/{_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 202)
            self.assertEqual(data['status'], 'success')

    def test_delete_alloy_non_existing(self):
        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)

            _id = str(ObjectId())

            res = client.delete(
                f'/v1/sim/global/alloys/{_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['message'], 'Alloy not found.')
            self.assertEqual(data['status'], 'fail')

    def test_invalid_request_object_id(self):
        """Error if we send an invalid ObjectId to the ones that require."""
        alloy_data = {
            'name': 'Alloy-101',
            'compositions': [{
                'symbol': 'C',
                'weight': 2.0
            }]
        }

        with app.test_client() as client:
            test_login(client, self.okoye.email, self._okoye_pw)
            _id = 123456789

            res = client.delete(
                f'/v1/sim/global/alloys/{_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')

            res = client.put(
                f'/v1/sim/global/alloys/{_id}',
                data=json.dumps(alloy_data),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assertEqual(data['status'], 'fail')

            res = client.get(
                f'/v1/sim/global/alloys/{_id}',
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid ObjectId.')


if __name__ == '__main__':
    unittest.main()
