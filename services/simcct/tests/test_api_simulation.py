# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.17'
"""test_api_simulation.py: 

{Description}
"""

import unittest
from pathlib import Path

from bson import ObjectId
from flask import current_app as app
from flask import json, session

from tests.test_api_base import BaseTestCase
from sim_app.schemas import AlloySchema, ConfigurationsSchema
from sim_app.app import BASE_DIR


_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSimulationService(BaseTestCase):

    def login_client(self, client):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = ConfigurationsSchema().load(test_json['configurations'])
        alloy = AlloySchema().load({
                'name': 'Arc_Stark',
                'compositions': test_json['compositions']
        })
        comp = {
            'alloy': alloy,
            'alloy_type': 'parent'
        }

        token = 'ABCDEFGHIJKLMOPQRSTUVWXYZ123'
        _id = ObjectId()

        sess_res = client.post(
            '/session',
            data=json.dumps(
                {
                    '_id': str(_id),
                    'last_configurations': configs,
                    'last_compositions': comp
                }
            ),
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        data = json.loads(sess_res.data.decode())
        session_store = session.get(f'{token}:alloy')
        self.assertEqual(data['status'], 'success')
        self.assertTrue(sess_res.status_code == 201)
        self.assertEqual(comp['alloy'], session_store)

        return configs, comp, token

    # def test_simulate(self):
    #     with app.test_client() as client:
    #         client.post('/simulate')


if __name__ == '__main__':
    unittest.main()

# 
