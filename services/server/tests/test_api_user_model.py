# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_user_model.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.05'

"""test_api_user_model.py: 

{Description}
"""

import unittest
import json

from bson.son import SON
from mongoengine.errors import ValidationError, NotUniqueError

from tests.test_api_base import BaseTestCase
from api.models import User, PasswordValidationError


class TestUserModel(BaseTestCase):
    def test_add_User(self):
        user = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('IAmIronMan')
        user.save()
        self.assertTrue(user.id)
        self.assertEqual('codeninja55', user.username)
        self.assertEqual('andrew@neuraldev.io', user.email)
        self.assertEqual(user.last_updated, user.created)
        self.assertIsNone(user.last_login)
        self.assertTrue(user.active)
        self.assertTrue(user.password)

    def test_email_validation(self):
        user = User(username='Fake Twtitter', email='russianfakeemail@russia')
        user.set_password('IAmIronMan')
        with self.assertRaises(ValidationError):
            user.save()

    def test_password_validation(self):
        user = User(username='Fake User', email='russianfakeemail@russia.com')
        with self.assertRaises(PasswordValidationError):
            user.save()

    def test_add_user_duplicate_email(self):
        user = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('IAmIronMan')
        user.save()
        duplicate_user = User(username='codeninja55', email='andrew@neuraldev.io')
        duplicate_user.set_password('IThinkIAmIronMan')
        with self.assertRaises(NotUniqueError):
            duplicate_user.save()

    def test_to_dict(self):
        user = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('IAmIronMan')
        user.save()
        self.assertTrue(user.to_dict(), dict)

    def test_to_json(self):
        user = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('IAmIronMan')
        user.save()
        user_json = json.loads(user.to_json())  # mongoengine returns a string
        self.assertIsInstance(user.to_mongo(), SON)
        self.assertTrue(user.to_json(), str)
        self.assertTrue(user.to_dict(), dict)
        self.assertEqual(user_json['username'], 'codeninja55')

    def test_passwords_are_random(self):
        user_one = User(username='codeninja55', email='andrew@neuraldev.io')
        user_one.set_password('youknotwhatitis')
        user_two = User(username='cn55', email='andrew@codeninja55.me')
        user_two.set_password('youknotwhatitwas')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = user_one = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('youknotwhatitis')
        user.save()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = user_one = User(username='codeninja55', email='andrew@neuraldev.io')
        user.set_password('youknotwhatitis')
        user.save()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(User.decode_auth_token(auth_token), str(user.id))


if __name__ == '__main__':
    unittest.main()
