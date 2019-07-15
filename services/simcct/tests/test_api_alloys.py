# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.14'
"""test_api_alloys.py: 

{Description}
"""

import json
import unittest
from pathlib import Path

from bson import ObjectId
from flask import current_app as app

from sim_app.app import BASE_DIR
from tests.test_api_base import BaseTestCase
from sim_app.schemas import ElementSchema

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestAlloyService(BaseTestCase):
    def test_create_alloy(self):
        """Ensure we can create an alloy."""
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        with app.test_client() as client:
            res = client.post(
                '/alloys',
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
            self.assertTrue(data['_id'])
            self.assertTrue(ObjectId.is_valid(data['_id']))

    def test_get_all_alloys(self):
        """Ensure we can get all alloys."""

        with app.test_client() as client:
            res = client.get('/alloys', content_type='application/json')
            data = json.loads(res.data.decode())

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['alloys'])


if __name__ == '__main__':
    unittest.main()
