# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_user_alloys_service.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.02'
"""test_api_user_alloys_service.py: 

Unit Testing the User Alloy Service.
"""

import unittest
from pathlib import Path

from bson import ObjectId
from flask import current_app as app
from flask import json

from tests.test_api_base import BaseTestCase
from configs.settings import BASE_DIR
from users_app.models import User

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'seed_alloy_data.json'

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
        }
    ]
}


class TestUserAlloyService(BaseTestCase):
    user = None

    def setUp(self) -> None:
        self.user = User(
            first_name='Morgan',
            last_name='Stark',
            email='morgan@starkindustries.com'
        )
        self.user.set_password('IronHeart!')
        self.user.verified = True
        self.user.save()

    def tearDown(self) -> None:
        self.user.delete()

    @staticmethod
    def login(
        client, email='morgan@starkindustries.com', password='IronHeart!'
    ):
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

    def test_create_alloy(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            res = client.post(
                '/user/alloys',
                data=json.dumps(alloy_data),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            copy_data = alloy_data.copy()
            copy_data['_id'] = data['data']['_id']
            self.assertEqual(data['data'], copy_data)

    def test_create_unauthorized(self):
        with app.test_client() as client:
            res = client.post(
                '/user/alloys',
                data=json.dumps(alloy_data),
                headers={'Authorization': 'Bearer BadToken!'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Invalid token. Please log in again.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_create_empty_payload(self):
        with app.test_client() as client:
            token = self.login(client)

            res = client.post(
                '/user/alloys',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_invalid_payload_comps(self):
        with app.test_client() as client:
            token = self.login(client)

            invalid_alloy = {
                'name': 'Alloy_1',
                'compositions': {
                    "symbol": "C",
                    "weight": 0.0
                }
            }

            res = client.post(
                '/user/alloys',
                data=json.dumps(invalid_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = (
                'Compositions must be provided as a list of valid elements '
                'e.g. {"symbol": "C", "weight": 1.0}'
            )
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_invalid_missing_name(self):
        with app.test_client() as client:
            token = self.login(client)

            invalid_alloy = {'compositions': [{"symbol": "C", "weight": 0.0}]}

            res = client.post(
                '/user/alloys',
                data=json.dumps(invalid_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Name must be provided.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_invalid_empty_list(self):
        with app.test_client() as client:
            token = self.login(client)

            invalid_alloy = {'name': 'Alloy_1', 'compositions': []}

            res = client.post(
                '/user/alloys',
                data=json.dumps(invalid_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = (
                'Compositions must be provided as a list of valid elements '
                'e.g. {"symbol": "C", "weight": 1.0}'
            )
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_create_invalid_bad_elements(self):
        with app.test_client() as client:
            token = self.login(client)

            invalid_alloy = {
                'name': 'Alloy_1',
                'compositions': [{
                    'name': 'Carbon',
                    'weight': 0.0
                }]
            }

            res = client.post(
                '/user/alloys',
                data=json.dumps(invalid_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy validation error.')
            self.assertEqual(data['status'], 'fail')
            err = (
                'The fields "{\'name\'}" do not exist on the document '
                '"Element"'
            )
            self.assertEqual(data['error'], err)
            self.assert400(res)

    def test_create_invalid_elements_missing(self):
        with app.test_client() as client:
            token = self.login(client)

            invalid_alloy = {
                'name': 'Alloy_1',
                'compositions': [{
                    'weight': 0.0
                }]
            }

            res = client.post(
                '/user/alloys',
                data=json.dumps(invalid_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element error.')
            self.assertEqual(data['status'], 'fail')
            err = (
                'ValidationError (Element) (symbol.Field is required: '
                '["Element.symbol"]))'
            )
            self.assertEqual(data['error'], err)
            self.assert400(res)

    def test_retrieve_list(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            alloy_data2 = {
                'name':
                'Alloy-102',
                'compositions': [
                    {
                        "symbol": "C",
                        "weight": 0.044
                    },
                    {
                        "symbol": "Mn",
                        "weight": 1.73
                    },
                    {
                        "symbol": "Si",
                        "weight": 0.22
                    },
                ]
            }

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.saved_alloys.create(**alloy_data2)
            user.save()

            res = client.get(
                '/user/alloys',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            self.assertEqual(len(data['data']), 2)

    def test_retrieve_list_unauthorized(self):
        with app.test_client() as client:
            res = client.post(
                '/user/alloys',
                headers={'Authorization': 'Bearer HelloThere!'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Invalid token. Please log in again.'
            )
            self.assertEqual(data['status'], 'fail')

    def test_retrieve_single(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            alloy_data2 = {
                'name':
                'Alloy-102',
                'compositions': [
                    {
                        "symbol": "C",
                        "weight": 0.044
                    },
                    {
                        "symbol": "Mn",
                        "weight": 1.73
                    },
                    {
                        "symbol": "Si",
                        "weight": 0.22
                    },
                ]
            }

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.saved_alloys.create(**alloy_data2)
            user.save()
            _id = str(user.saved_alloys[0].oid)

            res = client.get(
                f'/user/alloys/{_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            copy_data = alloy_data.copy()
            copy_data['_id'] = data['data']['_id']
            self.assertEqual(data['data'], copy_data)

    def test_retrieve_single_first(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.save()
            _id = str(user.saved_alloys[0].oid)

            res = client.get(
                f'/user/alloys/{_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertTrue(data['data'])
            copy_data = alloy_data.copy()
            copy_data['_id'] = data['data']['_id']
            self.assertEqual(data['data'], copy_data)

    def test_retrieve_single_not_exist(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            _id = ObjectId()

            res = client.get(
                f'/user/alloys/{_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy does not exist.')
            self.assertEqual(data['status'], 'fail')
            self.assert404(res)

    def test_retrieve_single_invalid_objectid(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            res = client.get(
                '/user/alloys/cheeseburgers',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_delete_alloy(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            alloy_data2 = {
                'name':
                    'Alloy-102',
                'compositions': [
                    {
                        "symbol": "C",
                        "weight": 0.044
                    },
                    {
                        "symbol": "Mn",
                        "weight": 1.73
                    },
                    {
                        "symbol": "Si",
                        "weight": 0.22
                    },
                ]
            }

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.saved_alloys.create(**alloy_data2)
            user.save()
            _id = str(user.saved_alloys[0].oid)

            res = client.delete(
                f'/user/alloys/{_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 202)
            self.assertEqual(data['status'], 'success')
            user.reload()
            copy_data = alloy_data.copy()
            copy_data['_id'] = _id
            self.assertNotEqual(
                user.saved_alloys.first().to_dict(),
                copy_data
            )
            alloy_data2['_id'] = str(user.saved_alloys.first().oid)
            self.assertEqual(
                user.saved_alloys.first().to_dict(),
                alloy_data2
            )

    def test_delete_invalid_objectid(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            res = client.get(
                '/user/alloys/cheeseburgers',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_delete_alloy_no_exists(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            _id = ObjectId()

            res = client.delete(
                f'/user/alloys/{_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'No alloy found.')
            self.assertEqual(data['status'], 'fail')
            self.assert404(res)

    def test_delete_alloy_bad_id(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.save()
            _id = ObjectId()

            res = client.delete(
                f'/user/alloys/{_id}',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['message'], 'Alloy does not exist.')
            self.assertEqual(data['status'], 'fail')

    def test_update_empty_json(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            _id = ObjectId()

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_update_bad_objectid(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            res = client.patch(
                f'/user/alloys/ironheart!',
                data=json.dumps(alloy_data),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid ObjectId.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_update_no_valid_keys(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            _id = ObjectId()

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps({'alloy_name': 'Wrong_Key', 'comps': []}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = ('Invalid keys in request payload (i.e. must be either "name"'
                   ' or "compositions").')
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_update_comps_not_list(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            _id = ObjectId()

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps({'compositions': {'symbol': 'C', 'weight': 1}}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = ('Compositions must be provided as a list of valid elements '
                   'e.g. {"symbol": "C", "weight": 1.0}')
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_update_non_existing(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            _id = ObjectId()

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(alloy_data),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'No alloys found.')
            self.assertEqual(data['status'], 'fail')
            self.assert404(res)

    def test_update_wrong_alloy(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.save()

            _id = ObjectId()

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(alloy_data),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy does not exist.')
            self.assertEqual(data['status'], 'fail')
            self.assert404(res)

    def test_update_invalid_alloy(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            # validation for schema correctness occurs before document access
            _id = ObjectId()

            updated_alloy = {
                'compositions': [
                    {"symbol": "C"},
                ]
            }

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(updated_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err = ('ValidationError (Element) (symbol.Field is required: '
                   '["Element.weight"])')
            self.assertIsNotNone(data.get('error', None))
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Invalid element error.')
            self.assertEqual(data['status'], 'fail')
            self.assertIsNone(data.get('data', None))
            self.assert400(res)

    def test_update_invalid_element_symbol(self):
        """Ensure that the symbol that is passed is not invalid according to
        our use of the Periodic Table symbol.
        """
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            # validation for schema correctness occurs before doc access
            _id = ObjectId()

            # Yes, MS is not an element symbol
            updated_alloy = {
                'compositions': [
                    {'symbol': 'MS', 'weight': 0.5},
                ]
            }

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(updated_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            # we want it to stop here because validation has not failed as we
            # expected it to.
            self.assertNotEqual(data['message'], 'No alloys found.')
            err = ('ValidationError (Element) (Field does not match a valid '
                   'element symbol in the Periodic Table: ["symbol"])')
            self.assertIsNotNone(data.get('error', None))
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Invalid element symbol error.')
            self.assertEqual(data['status'], 'fail')
            self.assertIsNone(data.get('data', None))
            self.assert400(res)

    def test_partial_update_name_only(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.save()

            _id = str(user.saved_alloys[0].oid)

            new_name = 'Alloy-New-101'
            updated_alloy = {
                'name': new_name
            }

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(updated_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data.get('data', None))
            self.assert200(res)
            expected_alloy = alloy_data.copy()
            expected_alloy['_id'] = data['data']['_id']
            expected_alloy['name'] = new_name
            self.assertEqual(data['data'], expected_alloy)

    def test_partial_update(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.save()

            _id = str(user.saved_alloys[0].oid)

            updated_alloy = {
                'compositions': [
                    {"symbol": "C", "weight": 0.5},
                    {"symbol": "Mn", "weight": 1.5}
                ]
            }

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(updated_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data.get('data', None))
            self.assert200(res)
            expected_alloy = alloy_data.copy()
            expected_alloy['_id'] = data['data']['_id']
            expected_alloy['compositions'][0]['weight'] = 0.5
            expected_alloy['compositions'][1]['weight'] = 1.5
            self.assertEqual(data['data'], expected_alloy)

    def test_partial_add(self):
        with app.test_client() as client:
            token = self.login(client)
            self.assertTrue(token)

            user = User.objects.get(email='morgan@starkindustries.com')
            user.saved_alloys.create(**alloy_data)
            user.save()

            _id = str(user.saved_alloys[0].oid)

            new_name = 'Alloy-New-101'
            new_elem = {"symbol": "Fe", "weight": 0.01}
            updated_alloy = {
                'name': new_name,
                'compositions': [new_elem]
            }

            res = client.patch(
                f'/user/alloys/{_id}',
                data=json.dumps(updated_alloy),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertIsNotNone(data.get('data', None))
            self.assert200(res)
            expected_alloy = alloy_data.copy()
            expected_alloy['_id'] = data['data']['_id']
            expected_alloy['name'] = new_name
            expected_alloy['compositions'].append(new_elem)
            self.assertEqual(data['data'], expected_alloy)


if __name__ == '__main__':
    unittest.main()
