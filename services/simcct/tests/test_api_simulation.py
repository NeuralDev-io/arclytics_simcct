# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__status__ = 'development'
__date__ = '2019.07.17'

import os
import unittest
from copy import deepcopy
from pathlib import Path

from flask import json
from mongoengine import get_db

from arc_logging import AppLogger
from sim_api.models import User
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

logger = AppLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'sim_configs.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    test_json = json.load(f)

ALLOY_STORE = {
    'alloy_option': 'single',
    'alloys': {
        'parent': {
            'name': 'Arc_Stark',
            'compositions': test_json['compositions']
        },
        'weld': None,
        'mix': None
    }
}

CONFIGS = test_json['configurations']


class TestSimulationService(BaseTestCase):
    _email = None
    _user_pw = 'IMissThor!!!'
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        assert app.config['TESTING'] is True

        cls.user = User(
            **{
                'email': 'janefoster@arclytics.io',
                'first_name': 'Jane',
                'last_name': 'Foster',
            }
        )
        cls.user.set_password(cls._user_pw)
        cls.user.verified = True
        cls.user.save()
        cls._email = cls.user.email

        mongo = get_db('default')
        user = mongo.users.find_one({'email': 'janefoster@arclytics.io'})
        assert user is not None

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def test_simulate_with_login(self):
        """Ensure there is a successful simulation get request."""
        configs = deepcopy(CONFIGS)
        with app.test_client() as client:
            test_login(client, self._email, self._user_pw)

            # We need to update Ae, MS, and BS in the configs
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assert200(res)

            configs.update(
                {
                    'ae1_temp': data['data']['ae1_temp'],
                    'ae3_temp': data['data']['ae3_temp'],
                }
            )

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assert200(res)

            configs.update(
                {
                    'ms_temp': data['data']['ms_temp'],
                    'ms_rate_param': data['data']['ms_rate_param'],
                }
            )

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assert200(res)

            configs.update({'bs_temp': data['data']['bs_temp']})

            # Now we can run
            res = client.post(
                '/v1/sim/simulate',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'configurations': configs
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            # logger.debug(data)
            self.assertFalse(data.get('message', None))
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            self.assertEqual(
                len(data['data']['CCT']['ferrite_nucleation']['time']),
                len(data['data']['CCT']['ferrite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['ferrite_completion']['time']),
                len(data['data']['CCT']['ferrite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['pearlite_nucleation']['time']),
                len(data['data']['CCT']['pearlite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['pearlite_completion']['time']),
                len(data['data']['CCT']['pearlite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['bainite_nucleation']['time']),
                len(data['data']['CCT']['bainite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['bainite_completion']['time']),
                len(data['data']['CCT']['bainite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['martensite']['time']),
                len(data['data']['CCT']['martensite']['temp'])
            )

    def test_ae3_equilibrium_results(self):
        with app.test_client() as client:
            test_login(client, self._email, self._user_pw)

            # We need to get Ae1 before we can run.
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertTrue(data.get('data'))
            self.assert200(res)
            ae1_temp = data['data']['ae1_temp']

            res = client.get(
                '/v1/sim/ae3equilibrium',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'ae1_temp': ae1_temp
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)

            ceut = float(data['data']['eutectic_composition_carbon'])
            xfe = float(data['data']['ferrite_phase_frac'])
            cf = float(data['data']['cf'])
            self.assertEqual(ceut, 0.83)
            self.assertAlmostEqual(xfe, 0.9462, 4)
            self.assertEqual(cf, 0.012)
            logger.debug(data['data']['results_plot'])


if __name__ == '__main__':
    unittest.main()
