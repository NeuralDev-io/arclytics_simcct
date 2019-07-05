# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""test_api_users.py: 

{Description}
"""

import json
import unittest

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from api.models import User

logger = AppLogger(__name__)


class TestUserService(BaseTestCase):
    """Tests for the User API service."""
    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        res = self.client.get('/users/ping')
        data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('pong', data['message'])

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'codeninja55',
                    'email': 'andrew@neuraldev.io',
                    'password': 'IAmIronMan'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('andrew@neuraldev.io was added', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have a email key."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'username': 'codeninja55', 'password': 'IAmIronMan'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'codeninja55',
                    'email': 'andrew@neuraldev.io',
                    'password': 'IAmIronMan'
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'codeninja55',
                    'email': 'andrew@neuraldev.io',
                    'password': 'IAmActuallyElonMusk'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Error, email exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_no_password(self):
        """Ensure error is throw if the user does not have a password."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'codeninja55',
                    'email': 'andrew@neuraldev.io'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('A user account must have a password.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure we can get a single user works as expected."""
        user = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('IAmIronMan')
        user.save()

        with self.client:
            resp = self.client.get('/users/{user_id}'.format(user_id=user.id))
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertIn('codeninja55', data['data']['username'])
            self.assertIn('andrew@neuraldev.io', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Invalid bson.ObjectId type.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            from bson import ObjectId
            id = ObjectId()
            response = self.client.get('/users/{}'.format(id))
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_all_users(self):
        """Ensure we can get all users."""
        tony = User(username='iron_man', email='tony@starkindustries.com')
        tony.set_password('IAmTheRealIronMan')
        tony.save()
        nat = User(username='black_widow', email='nat@shield.gov.us')
        nat.set_password('IveGotRedInMyLedger')
        nat.save()

        with self.client:
            resp = self.client.get('/users')
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('iron_man', data['data']['users'][0]['username'])
            self.assertIn('black_widow', data['data']['users'][1]['username'])
            self.assertIn('success', data['status'])


if __name__ == '__main__':
    unittest.main()
