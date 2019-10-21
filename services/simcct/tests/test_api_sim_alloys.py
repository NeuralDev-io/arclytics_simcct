# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.07.13'

import json
import unittest
from pathlib import Path

from mongoengine import get_db

from manage import BASE_DIR
from sim_api.models import User
from sim_api.schemas import AlloyStoreSchema, ConfigurationsSchema
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'tests' / 'sim_configs.json'

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


class TestSimAlloys(BaseTestCase):
    _email = None
    _user_pw = 'IllShowYouFerocity!@!@'
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        assert app.config['TESTING'] is True

        # Tony is an admin
        cls.user = User(
            **{
                'email': 'antman@avengers.io',
                'first_name': 'Hank',
                'last_name': 'Pym'
            }
        )
        cls.user.set_password(cls._user_pw)
        cls.user.verified = True

        configs = ConfigurationsSchema().load(test_json['configurations'])
        alloy_store = AlloyStoreSchema().load(ALLOY_STORE)

        cls.user.last_alloy_store = alloy_store
        cls.user.last_configuration = configs

        cls.user.save()
        cls._email = cls.user.email

        mongo = get_db('default')
        user = mongo.users.find_one({'email': 'antman@avengers.io'})
        assert user is not None

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def login_client(self, client):
        """Set up a User for the simulation."""
        test_login(client, self._email, self._user_pw)

    def test_post_alloy_missing_elements(self):
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/v1/sim/alloys/update',
                data=json.dumps(
                    {
                        'alloy_store': {
                            'alloy_option': 'single',
                            'alloys': {
                                'parent': {
                                    'name':
                                    'Bad Alloy',
                                    'compositions':
                                    [{
                                        'symbol': 'C',
                                        'weight': 0.7
                                    }]
                                }
                            }
                        },
                        'method': 'Li98',
                        'auto_calculate_ae': True
                    }
                ),
                content_type='application/json'
            )
            data = res.json
            self.assertEqual(data['message'], 'Missing element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_post_alloy_all_elements(self):
        with app.test_client() as client:
            self.login_client(client)

            good_comp = [
                {
                    'symbol': 'C',
                    'weight': 0.044
                },
                {
                    'symbol': 'Mn',
                    'weight': 0.0
                },
                {
                    'symbol': 'Ni',
                    'weight': 0.0
                },
                {
                    'symbol': 'Cr',
                    'weight': 0.0
                },
                {
                    'symbol': 'Mo',
                    'weight': 0.0
                },
                {
                    'symbol': 'Si',
                    'weight': 0.0
                },
                {
                    'symbol': 'Co',
                    'weight': 0.0
                },
                {
                    'symbol': 'W',
                    'weight': 0.0
                },
                {
                    'symbol': 'As',
                    'weight': 0.0
                },
                {
                    'symbol': 'Fe',
                    'weight': 0.0
                },
            ]

            res = client.post(
                '/v1/sim/alloys/update',
                data=json.dumps(
                    {
                        'alloy_store': {
                            'alloy_option': 'single',
                            'alloys': {
                                'parent': {
                                    'name': 'Good comp',
                                    'compositions': good_comp
                                }
                            }
                        },
                        'method': 'Li98',
                        'auto_calculate_ae': True,
                        'auto_calculate_ms': True,
                        'auto_calculate_bs': True,
                    }
                ),
                content_type='application/json'
            )
            data = res.json
            trans_temps = data['data']
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 200)
            self.assertAlmostEqual(trans_temps['ms_temp'], 520.388, 2)
            self.assertAlmostEqual(trans_temps['ms_rate_param'], 0.0219292, 2)
            self.assertAlmostEqual(trans_temps['bs_temp'], 634.448, 2)
            self.assertAlmostEqual(trans_temps['ae1_temp'], 719.259259259, 2)
            self.assertAlmostEqual(trans_temps['ae3_temp'], 887.130506988, 2)

    def test_on_comp_change_auto_update_temps(self):
        """Ensure if we update compositions schema we also auto update."""
        with app.test_client() as client:
            self.login_client(client)

            # Now we change the compositions and make sure it's all updated
            # with the composition change
            new_alloy_store = {
                'alloy_option': 'single',
                'alloys': ALLOY_STORE['alloys']
            }

            new_parent_comp: dict = new_alloy_store['alloys'].get('parent')
            new_parent_comp['compositions'][0]['weight'] = 0.050  # carbon
            new_parent_comp['compositions'][1]['weight'] = 1.6  # manganese
            req_alloy = AlloyStoreSchema().load(new_alloy_store)

            res = client.post(
                '/v1/sim/alloys/update',
                data=json.dumps(
                    {
                        'alloy_store': req_alloy,
                        'method': 'Li98',
                        'auto_calculate_ae': True,
                        'auto_calculate_ms': True,
                        'auto_calculate_bs': True
                    }
                ),
                content_type='application/json'
            )
            data = res.json

            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])

            # ANSTO SimCCT results
            ms_temp = 465.6272
            ms_rate_param = 0.02069
            bs_temp = 567.454
            ae1_temp = 702.7388
            ae3_temp = 847.1215

            self.assertAlmostEqual(data['data']['ms_temp'], ms_temp, 4)
            self.assertAlmostEqual(
                data['data']['ms_rate_param'], ms_rate_param, 4
            )
            self.assertAlmostEqual(data['data']['bs_temp'], bs_temp, 2)
            self.assertAlmostEqual(data['data']['ae1_temp'], ae1_temp, 2)
            self.assertAlmostEqual(data['data']['ae3_temp'], ae3_temp, 2)


if __name__ == '__main__':
    unittest.main()
