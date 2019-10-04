# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_user_model.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.07.05'
"""test_api_user_model.py: 

{Description}
"""

import os
import json
import unittest
from pathlib import Path

import mongoengine
from bson.son import SON
from mongoengine import get_db
from mongoengine.errors import ValidationError, NotUniqueError

from tests.test_api_base import BaseTestCase
from sim_api.models import User
from sim_api.extensions.utilities import PasswordValidationError

_TEST_CONFIGS_PATH = Path(os.getcwd()) / 'tests' / 'sim_configs.json'


class TestUserModel(BaseTestCase):
    """Run direct tests on the User model without an API call."""
    def tearDown(self) -> None:
        db = get_db('default')
        self.assertTrue(db.name, 'arc_test')
        db.users.drop()

    def test_user_model_schema(self):
        self.assertIsInstance(User.__base__, mongoengine.Document.__class__)
        self.assertIsInstance(User.email, mongoengine.EmailField)
        self.assertIsInstance(User.password, mongoengine.StringField)
        self.assertIsInstance(User.first_name, mongoengine.StringField)
        self.assertIsInstance(User.last_name, mongoengine.StringField)
        self.assertIsInstance(User.profile, mongoengine.EmbeddedDocumentField)
        self.assertIsInstance(
            User.admin_profile, mongoengine.EmbeddedDocumentField
        )
        self.assertIsInstance(User.last_configuration, mongoengine.DictField)
        self.assertIsInstance(User.last_alloy_store, mongoengine.DictField)
        self.assertIsInstance(
            User.last_simulation_results, mongoengine.DictField
        )
        self.assertIsInstance(
            User.saved_alloys, mongoengine.EmbeddedDocumentListField
        )
        self.assertIsInstance(User.active, mongoengine.BooleanField)

    def test_password_validation_error(self):
        err = PasswordValidationError()
        self.assertTrue(PasswordValidationError.__base__ is Exception)
        self.assertIn('A password must be set before saving.', str(err))

    def test_add_user(self):
        user = User(
            **{
                'email': 'umm_baku@wakanda.io',
                'first_name': "M'Baku",
                'last_name': 'Jabari'
            }
        )
        user.set_password('WeAreVegetarians')
        user.save()
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, "M'Baku")
        self.assertEqual(user.last_name, 'Jabari')
        self.assertEqual('umm_baku@wakanda.io', user.email)
        self.assertEqual(user.last_updated, user.created)
        self.assertIsNone(user.last_login)
        self.assertTrue(user.active)
        self.assertTrue(user.password)

    def test_add_configuration(self):
        """Test how we can add configurations as an embedded document."""
        user = User(
            **{
                'email': 'eric@shield.gov.us',
                'first_name': 'Eric',
                'last_name': 'Selvig'
            }
        )
        user.set_password('BifrostIsReal')

        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)
        test_configs = test_json['configurations']

        user.last_configuration = test_configs
        user.save()

        self.assertEqual(user.last_configuration['method'], 'Li98')
        self.assertEqual(user.last_configuration['grain_size'], 8.0)
        self.assertEqual(user.last_configuration['nucleation_start'], 1.0)
        self.assertEqual(user.last_configuration['nucleation_finish'], 99.9)
        self.assertEqual(user.last_configuration['start_temp'], 900)
        self.assertEqual(user.last_configuration['cct_cooling_rate'], 10)

    # noinspection PyTypeChecker
    def test_add_compositions(self):
        """Test how we can add the compositions as an embedded document."""
        user = User(
            **{
                'email': 'eric@shield.gov.us',
                'first_name': 'Eric',
                'last_name': 'Selvig'
            }
        )
        user.set_password('BifrostIsReal')

        alloy_store = {
            'alloy_option': 'single',
            'alloys': {
                'parent': {
                    'name':
                    'Selvigium',
                    'compositions': [
                        {
                            'symbol': 'C',
                            'weight': 0.044
                        }, {
                            'symbol': 'Mn',
                            'weight': 1.73
                        }
                    ]
                },
                'weld': None,
                'mix': None
            }
        }
        user.last_alloy_store = alloy_store
        user.cascade_save()

        alloy = user.last_alloy_store['alloys']['parent']
        self.assertEqual(alloy['name'], 'Selvigium')
        self.assertEqual(alloy['compositions'][0]['symbol'], 'C')
        self.assertEqual(alloy['compositions'][0]['weight'], 0.044)
        self.assertEqual(alloy['compositions'][1]['symbol'], 'Mn')
        self.assertEqual(alloy['compositions'][1]['weight'], 1.73)

    # noinspection PyTypeChecker
    def test_add_compositions_from_json(self):
        """Ensure we can loop a JSON-converted dict to create a compositions."""
        user = User(
            **{
                'email': 'eric@shield.gov.us',
                'first_name': 'Eric',
                'last_name': 'Selvig'
            }
        )
        user.set_password('BifrostIsReal')

        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        new_comp_inst = {
            'name': 'Selvigium',
            'compositions': test_json['compositions']
        }

        alloy_store = {
            'alloy_option': 'single',
            'alloys': {
                'parent': new_comp_inst,
                'weld': None,
                'mix': None
            }
        }

        user.last_alloy_store = alloy_store
        user.cascade_save()

        comp = user.last_alloy_store['alloys']['parent']
        self.assertEqual(comp['name'], 'Selvigium')
        self.assertEqual(comp['compositions'][0]['symbol'], 'C')
        self.assertEqual(comp['compositions'][0]['weight'], 0.044)
        self.assertEqual(comp['compositions'][1]['symbol'], 'Mn')
        self.assertEqual(comp['compositions'][1]['weight'], 1.73)
        self.assertEqual(comp['compositions'][2]['symbol'], 'Si')
        self.assertEqual(comp['compositions'][2]['weight'], 0.22)

    def test_email_validation(self):
        user = User(
            **{
                'email': 'russianfakeemail@russia',
                'first_name': 'Vlad',
                'last_name': 'Ruskie'
            }
        )
        user.set_password('IAmIronMan')
        with self.assertRaises(ValidationError):
            user.save()

    def test_password_validation(self):
        user = User(
            **{
                'email': 'russianfakeemail@russia.com',
                'first_name': 'Real',
                'last_name': 'Trumpie'
            }
        )
        with self.assertRaises(PasswordValidationError):
            user.save()

    def test_add_user_duplicate_email(self):
        user = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )
        user.set_password('IAmIronMan')
        user.save()
        duplicate_user = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )
        duplicate_user.set_password('IThinkIAmIronMan')
        with self.assertRaises(NotUniqueError):
            duplicate_user.save()

    def test_to_dict(self):
        user = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )
        user.set_password('IAmIronMan')
        user.save()
        user_dict = user.to_dict()
        self.assertTrue(user_dict, dict)

    def test_to_json(self):
        user = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )
        user.set_password('IAmIronMan')
        user.save()
        self.assertIsInstance(user.to_mongo(), SON)
        self.assertTrue(user.to_json(), str)
        self.assertTrue(user.to_dict(), dict)

    def test_passwords_are_random(self):
        user_one = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )

        user_one.set_password('youknotwhatitwas')
        user_two = User(
            **{
                'email': 'ned@avengers.me',
                'first_name': 'Ned',
                'last_name': 'Leeds'
            }
        )
        user_two.set_password('youknotwhatitwas')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )
        user.set_password('PeterTingle!')
        user.save()
        from sim_api.auth_service import AuthService
        auth_token = AuthService().encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        """Ensure that a JWT auth token is generated properly."""
        user = User(
            **{
                'email': 'spidey@avengers.io',
                'first_name': 'Peter',
                'last_name': 'Parker'
            }
        )
        user.set_password('PeterTingle!')
        user.save()
        from sim_api.auth_service import AuthService
        auth_token = AuthService().encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(AuthService().decode_auth_token(auth_token), user.id)


if __name__ == '__main__':
    unittest.main()
