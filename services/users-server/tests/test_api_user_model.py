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
from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from mongoengine.errors import ValidationError, NotUniqueError

from tests.test_api_base import BaseTestCase
from api import models
from api.models import User, PasswordValidationError, USERS


class TestUserModel(BaseTestCase):
    def test_user_model_schema(self):
        self.assertIsInstance(User.__base__, Document.__class__)
        self.assertIsInstance(User.email, EmailField)
        self.assertIsInstance(User.username, StringField)
        self.assertIsInstance(User.active, BooleanField)

    def test_user_type_choices(self):
        admin_choice = USERS[0]
        normal_choice = USERS[1]
        self.assertEqual(admin_choice[0], '1')
        self.assertEqual(admin_choice[1], 'ADMIN')
        self.assertEqual(normal_choice[0], '2')
        self.assertEqual(normal_choice[1], 'USER')

    def test_password_validation_error(self):
        err = PasswordValidationError()
        self.assertTrue(PasswordValidationError.__base__ is Exception)
        self.assertIn('A password must be set before saving.', str(err))

    def test_add_user(self):
        user = models.User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
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
        user = User(
            username='Fake Twtitter',
            email='russianfakeemail@russia',
            first_name='Vlad',
            last_name='Ruskie'
        )
        user.set_password('IAmIronMan')
        with self.assertRaises(ValidationError):
            user.save()

    def test_password_validation(self):
        user = User(
            username='Fake User',
            email='russianfakeemail@russia.com',
            first_name='Real',
            last_name='Trumpie'
        )
        with self.assertRaises(PasswordValidationError):
            user.save()

    def test_add_user_duplicate_email(self):
        user = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('IAmIronMan')
        user.save()
        duplicate_user = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        duplicate_user.set_password('IThinkIAmIronMan')
        with self.assertRaises(NotUniqueError):
            duplicate_user.save()

    def test_to_dict(self):
        user = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('IAmIronMan')
        user.save()
        user_dict = user.to_dict()
        self.assertTrue(user_dict['_id'], user.id)
        self.assertTrue(user_dict, dict)

    def test_to_json(self):
        user = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('IAmIronMan')
        user.save()
        user_json = json.loads(user.to_json())  # mongoengine returns a string
        self.assertIsInstance(user.to_mongo(), SON)
        self.assertTrue(user.to_json(), str)
        self.assertTrue(user.to_dict(), dict)
        self.assertEqual(user_json['username'], 'codeninja55')

    def test_passwords_are_random(self):
        user_one = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )

        user_one.set_password('youknotwhatitis')
        user_two = User(
            username='cn55',
            email='andrew@codeninja55.me',
            first_name='Andrew',
            last_name='Che'
        )
        user_two.set_password('youknotwhatitwas')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = user_one = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('youknotwhatitis')
        user.save()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = user_one = User(
            username='codeninja55',
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('youknotwhatitis')
        user.save()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(User.decode_auth_token(auth_token), user.id)


if __name__ == '__main__':
    unittest.main()
