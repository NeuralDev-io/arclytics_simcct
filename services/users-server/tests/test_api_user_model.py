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

import os
import json
import unittest
from pathlib import Path

from bson.son import SON
from mongoengine import Document, StringField, EmailField, BooleanField
from mongoengine.errors import ValidationError, NotUniqueError

from tests.test_api_base import BaseTestCase
from users_api.models.models import (User, PasswordValidationError,
                                     USERS, Configuration, Element,
                                     Compositions)


_TEST_CONFIGS_PATH = Path(os.getcwd()) / 'tests' / 'sim_configs.json'


class TestUserModel(BaseTestCase):
    """Run direct tests on the User model without an API call."""

    def test_user_model_schema(self):
        self.assertIsInstance(User.__base__, Document.__class__)
        self.assertIsInstance(User.email, EmailField)
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
        user = User(
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('IAmIronMan')
        user.save()
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Andrew')
        self.assertEqual(user.last_name, 'Che')
        self.assertEqual('andrew@neuraldev.io', user.email)
        self.assertEqual(user.last_updated, user.created)
        self.assertIsNone(user.last_login)
        self.assertTrue(user.active)
        self.assertTrue(user.password)

    def test_add_configuration(self):
        """Test how we can add configurations as an embedded document."""
        user = User(
            email='eric@shield.gov.us',
            first_name='Eric',
            last_name='Selvig'
        )
        user.set_password('BifrostIsReal')

        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)
        test_configs = test_json['configurations']

        config_inst = Configuration(**test_configs)
        user.last_configuration = config_inst
        user.cascade_save()

        self.assertEqual(user.last_configuration.method, 'Li98')
        self.assertEqual(user.last_configuration.grain_size, 8.0)
        self.assertEqual(user.last_configuration.grain_size_type, 'ASTM')
        self.assertEqual(user.last_configuration.nucleation_start, 1.0)
        self.assertEqual(user.last_configuration.nucleation_finish, 99.9)
        self.assertEqual(user.last_configuration.ms_undercool, 100.0)
        self.assertEqual(user.last_configuration.start_temp, 900)
        self.assertEqual(user.last_configuration.cct_cooling_rate, 10)

    def test_add_compositions(self):
        """Test how we can add the compositions as an embedded document."""
        user = User(
            email='eric@shield.gov.us',
            first_name='Eric',
            last_name='Selvig'
        )
        user.set_password('BifrostIsReal')

        elem1 = Element(name='carbon', symbol='cx', weight=0.044)
        elem2 = Element(name='manganese', symbol='mn', weight=1.73)
        comp = Compositions()
        comp.comp.append(elem1)
        comp.comp.append(elem2)
        user.last_compositions = comp
        user.cascade_save()

        self.assertEqual(user.last_compositions.comp[0]['name'], 'carbon')
        self.assertEqual(user.last_compositions.comp[0]['weight'], 0.044)
        self.assertEqual(user.last_compositions.comp[1]['name'], 'manganese')
        self.assertEqual(user.last_compositions.comp[1]['weight'], 1.73)

    def test_add_compositions_from_json(self):
        """Ensure we can loop a JSON-converted dict to create a compositions."""
        user = User(
            email='eric@shield.gov.us',
            first_name='Eric',
            last_name='Selvig'
        )
        user.set_password('BifrostIsReal')

        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)
        test_comp = test_json['compositions']

        new_comp_inst = Compositions()
        for e in test_comp:
            elem_inst = Element(**e)
            new_comp_inst.comp.append(elem_inst)

        user.last_compositions = new_comp_inst
        user.cascade_save()

        self.assertEqual(user.last_compositions.comp[0]['name'], 'carbon')
        self.assertEqual(user.last_compositions.comp[0]['symbol'], 'cx')
        self.assertEqual(user.last_compositions.comp[0]['weight'], 0.044)
        self.assertEqual(user.last_compositions.comp[1]['name'], 'manganese')
        self.assertEqual(user.last_compositions.comp[1]['symbol'], 'mn')
        self.assertEqual(user.last_compositions.comp[1]['weight'], 1.73)
        self.assertEqual(user.last_compositions.comp[2]['name'], 'silicon')
        self.assertEqual(user.last_compositions.comp[2]['symbol'], 'si')
        self.assertEqual(user.last_compositions.comp[2]['weight'], 0.22)

    def test_email_validation(self):
        user = User(
            email='russianfakeemail@russia',
            first_name='Vlad',
            last_name='Ruskie'
        )
        user.set_password('IAmIronMan')
        with self.assertRaises(ValidationError):
            user.save()

    def test_password_validation(self):
        user = User(
            email='russianfakeemail@russia.com',
            first_name='Real',
            last_name='Trumpie'
        )
        with self.assertRaises(PasswordValidationError):
            user.save()

    def test_add_user_duplicate_email(self):
        user = User(
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('IAmIronMan')
        user.save()
        duplicate_user = User(
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        duplicate_user.set_password('IThinkIAmIronMan')
        with self.assertRaises(NotUniqueError):
            duplicate_user.save()

    def test_to_dict(self):
        user = User(
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
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )
        user.set_password('IAmIronMan')
        user.save()
        self.assertIsInstance(user.to_mongo(), SON)
        self.assertTrue(user.to_json(), str)
        self.assertTrue(user.to_dict(), dict)

    def test_passwords_are_random(self):
        user_one = User(
            email='andrew@neuraldev.io',
            first_name='Andrew',
            last_name='Che'
        )

        user_one.set_password('youknotwhatitwas')
        user_two = User(
            email='andrew@codeninja55.me',
            first_name='Andrew',
            last_name='Che'
        )
        user_two.set_password('youknotwhatitwas')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = User(
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
        user = User(
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
