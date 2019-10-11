# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------

__author__ = ['Andrew Che <@codeninja55>']
__status__ = 'development'
__date__ = '2019.07.13'

import json
import unittest
from copy import deepcopy
from pathlib import Path

import numpy as np
from mongoengine import get_db

from arc_logging import AppLogger
from manage import BASE_DIR
from sim_api.models import User
from sim_api.schemas import AlloyStoreSchema, ConfigurationsSchema
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

logger = AppLogger(__name__)

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'tests' / 'sim_configs.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    test_json = json.load(f)

ALLOY_STORE = {
    'alloy_option': 'single',
    'alloys': {
        'parent': {
            'name': 'Arc_Stark',
            'compositions': test_json['compositions']
        }
    }
}

CONFIGS = test_json['configurations']


# noinspection PyTypeChecker
class TestSimConfigurations(BaseTestCase):

    # Note:
    #  - We can treat the session stores of the compositions and configurations
    #    as always being the one that's displayed on the Client UI.

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
        store_dict = {
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
        alloy_store = AlloyStoreSchema().load(store_dict)

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

    def logout_client(self, client):
        resp_login = client.get(
            '/v1/sim/auth/logout',
            content_type='application/json',
            environ_base={'REMOTE_ADDR': '127.0.0.1'}
        )
        self.assertStatus(resp_login, 202)

    def test_auto_update_ms_invalid_payloads(self):
        """Ensure we get the correct error messages for invalid payloads."""
        with app.test_client() as client:
            self.login_client(client)

            # Empty payload
            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # No alloy store payload
            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps({'method': 'Li98'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy store required.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # No method payload
            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps({'alloy_store': ALLOY_STORE}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Method required.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Wrong method payload
            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'LiAndKirkaldy',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = 'Method must be one of ["Li98" | "Kirkaldy83"].'
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_auto_update_ms_invalid_alloys(self):
        """Ensure we get the correct error messages for bad alloy payloads."""
        with app.test_client() as client:
            self.login_client(client)

            # Missing carbon elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'].pop(0)

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Missing element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad symbol elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0]['symbol'] = 'Cx'

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element symbol error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad Carbon weight elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0]['weight'] = 0.9

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element weight error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad symbol key elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0].pop('symbol')

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_auto_update_ms(self):
        """Ensure we get the correct calculations for MS given the alloy."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            ms_temp = np.float32(data['data']['ms_temp'])
            ms_rate_param = np.float32(data['data']['ms_rate_param'])
            self.assertAlmostEqual(ms_temp, 464.1792, 2)
            self.assertAlmostEqual(ms_rate_param, 0.020691, 2)

    def test_auto_update_ms_kirkaldy_method(self):
        """Ensure we get the correct calculations for MS with Kirkaldy83."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'method': 'Kirkaldy83',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            ms_temp = np.float32(data['data']['ms_temp'])
            ms_rate_param = np.float32(data['data']['ms_rate_param'])
            self.assertAlmostEqual(ms_temp, 477.5753, 2)
            self.assertAlmostEqual(ms_rate_param, 0.02069, 2)

    def test_deprecated_update_ms(self):
        """Check that updating Ms has been deprecated."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/v1/sim/configs/ms',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Method Not Allowed.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 405)

    def test_auto_update_bs_invalid_payloads(self):
        """Ensure we get the correct error messages for invalid payloads."""
        with app.test_client() as client:
            self.login_client(client)

            # Empty payload
            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # No alloy store payload
            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps({'method': 'Li98'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy store required.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # No method payload
            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps({'alloy_store': ALLOY_STORE}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Method required.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Wrong method payload
            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'LiAndKirkaldy',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = 'Method must be one of ["Li98" | "Kirkaldy83"].'
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_auto_update_bs_invalid_alloys(self):
        """Ensure we get the correct error messages for bad alloy payloads."""
        with app.test_client() as client:
            self.login_client(client)

            # Missing carbon elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'].pop(0)

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Missing element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad symbol elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0]['symbol'] = 'Cx'

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element symbol error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad Carbon weight elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0]['weight'] = 0.9

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element weight error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad symbol key elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0].pop('symbol')

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_auto_update_bs(self):
        """Ensure we get the correct calculations for BS given the alloy."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            ms_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(ms_temp, 563.2208, 2)

    def test_auto_update_bs_kirkaldy_method(self):
        """Ensure we get the correct calculations for BS given Kirkaldy83
        method testing configs and the testing compositions.
        """
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'method': 'Kirkaldy83',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            bs_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(bs_temp, 565.723, 2)

    def test_deprecated_update_bs(self):
        """Check that updating Bs has been deprecated."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/v1/sim/configs/ae',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Method Not Allowed.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 405)

    def test_auto_update_ae_invalid_payloads(self):
        """Ensure we get the correct error messages for invalid payloads."""
        with app.test_client() as client:
            self.login_client(client)

            # Empty payload
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # No alloy store payload
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps({'method': 'Li98'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Alloy store required.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # No method payload
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps({'alloy_store': ALLOY_STORE}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Method required.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Wrong method payload
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'method': 'LiAndKirkaldy',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = 'Method must be one of ["Li98" | "Kirkaldy83"].'
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_auto_update_ae_invalid_alloys(self):
        """Ensure we get the correct error messages for bad alloy payloads."""
        with app.test_client() as client:
            self.login_client(client)

            # Missing carbon elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'].pop(0)

            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Missing element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad symbol elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0]['symbol'] = 'Cx'

            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element symbol error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad Carbon weight elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0]['weight'] = 0.9

            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element weight error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # Bad symbol key elements
            alloy_store = deepcopy(ALLOY_STORE)
            alloy_store['alloys']['parent']['compositions'][0].pop('symbol')

            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': alloy_store
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid element error.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_auto_update_ae(self):
        """Ensure we get the correct calculations for Ae1 and Ae3."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'method': 'Li98',
                        'alloy_store': ALLOY_STORE
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            ae1 = np.float32(data['data']['ae1_temp'])
            ae3 = np.float32(data['data']['ae3_temp'])
            self.assertAlmostEqual(ae1, 700.8947, 2)
            self.assertAlmostEqual(ae3, 845.8189, 2)

    def test_deprecated_update_ae(self):
        """Check that updating Ae has been deprecated."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/v1/sim/configs/ae',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Method Not Allowed.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 405)


if __name__ == '__main__':
    unittest.main()
