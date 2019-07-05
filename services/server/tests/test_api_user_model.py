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
from pymongo.errors import DuplicateKeyError
from mongoengine.errors import ValidationError, NotUniqueError

from tests.test_api_base import BaseTestCase
from api.models import User


class TestUserModel(BaseTestCase):
    def test_add_User(self):
        user = User(
            username='codeninja55',
            email='andrew@neuraldev.io'
        )
        user.save()
        self.assertTrue(user.id)
        self.assertEqual('codeninja55', user.username)
        self.assertEqual('andrew@neuraldev.io', user.email)
        self.assertIsNone(user.last_updated)
        self.assertIsNone(user.last_login)
        self.assertTrue(user.active)

    def test_add_user_duplicate_email(self):
        user = User(
            username='codeninja55',
            email='andrew@neuraldev.io'
        )
        user.save()
        duplicate_user = User(
            username='codeninja55',
            email='andrew@neuraldev.io'
        )
        with self.assertRaises(NotUniqueError):
            duplicate_user.save()

    def test_to_json(self):
        user = User(
            username='codeninja55',
            email='andrew@neuraldev.io'
        )
        user.save()
        user_json = json.loads(user.to_json())  # mongoengine returns a string
        self.assertIsInstance(user.to_mongo(), SON)
        self.assertTrue(user.to_json(), str)
        self.assertTrue(user.to_dict(), dict)
        self.assertEqual(user_json['username'], 'codeninja55')


if __name__ == '__main__':
    unittest.main()
