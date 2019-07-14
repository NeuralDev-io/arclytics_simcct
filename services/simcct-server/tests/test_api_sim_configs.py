# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.13'
"""test_api_sim_configs.py: 

{Description}
"""

import json
import unittest
import numpy as np
from pathlib import Path

from bson import ObjectId
from flask import session, current_app

from sim_api import BASE_DIR
from tests.test_api_base import BaseTestCase

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSimConfigurations(BaseTestCase):

    # NOTE:
    #  - We can treat the session stores of the compositions as always being
    #    the one that's displayed on the Client UI.
    #  - We may be able to do the same as above for configurations.

    def test_on_compositions_change(self):
        # 1. Pass all compositions?
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        comp = {'comp': test_json['compositions']}
        token = 'ThisIsATestToken'

        # with app.test_client() as client:
        #     res = client.post(
        #         '/configs/comp/update',
        #         data=json.dumps({
        #             'token': token,
        #             'compositions': comp
        #         }),
        #         content_type='application/json'
        #     )
        #     data = json.loads(res.data.decode())
        #     print(data)

    def test_auto_update_ms_bs(self):
        """Ensure we get the correct calculations for MS and BS given the
        testing configs and the testing compositions.
        """
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = test_json['configurations']
        comp = {'comp': test_json['compositions']}
        _id = ObjectId()
        token = 'ThisIsATestToken'

        with current_app.test_client() as client:
            sess_res = client.post(
                '/session',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'token': str(token),
                        'last_configurations': configs,
                        'last_compositions': comp
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(sess_res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_res.status_code == 201)

            res = client.post(
                '/configs/auto/ms-bs',
                data=json.dumps(
                    {
                        'auto_calculate_ms_bs': True,
                        'transformation_method': 'Li98',
                        'compositions': comp
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_ms_bs'])
            ms_temp = np.float32(data['data']['ms_temp'])
            bs_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(sess_store['ms_temp'], 464.1960, 4)
            self.assertAlmostEqual(sess_store['bs_temp'], 563.2380, 4)
            self.assertAlmostEqual(ms_temp, 464.1960, 4)
            self.assertAlmostEqual(bs_temp, 563.2380, 4)

    def test_auto_update_ae(self):
        """Ensure we get the correct calculations for Ae1 and Ae3 given the
        testing configs and the testing compositions.
        """
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = test_json['configurations']
        comp = {'comp': test_json['compositions']}
        _id = ObjectId()
        token = 'ThisIsATestToken'

        with current_app.test_client() as client:
            sess_res = client.post(
                '/session',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'token': str(token),
                        'last_configurations': configs,
                        'last_compositions': comp
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(sess_res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_res.status_code == 201)

            res = client.post(
                '/configs/auto/ae',
                data=json.dumps(
                    {
                        'auto_calculate_ae': True,
                        'compositions': comp
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_ae'])
            ae1 = np.float64(data['data']['ae1_temp'])
            ae3 = np.float64(data['data']['ae3_temp'])
            self.assertAlmostEqual(sess_store['ae1_temp'], 700.901962962963, 8)
            self.assertAlmostEqual(sess_store['ae3_temp'], 845.837961185399, 8)
            self.assertAlmostEqual(ae1, 700.90196296296301, 8)
            self.assertAlmostEqual(ae3, 845.83796118539999, 8)

    def test_auto_update_xfe_bad_ae1(self):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = test_json['configurations']
        comp = {'comp': test_json['compositions']}
        _id = ObjectId()
        token = 'ThisIsATestToken'

        with current_app.test_client() as client:
            sess_res = client.post(
                '/session',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'token': str(token),
                        'last_configurations': configs,
                        'last_compositions': comp
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(sess_res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_res.status_code == 201)

            res = client.post(
                '/configs/auto/xfe',
                data=json.dumps(
                    {
                        'auto_calculate_xfe': True,
                        'compositions': comp
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            msg = (
                'Ae1 must be more than zero to find the Equilibrium Phase '
                'Fraction.'
            )
            self.assertEqual(data['message'], msg)

    def test_auto_update_xfe(self):
        """Ensure we get the correct calculations for Xfe given the testing
        configs and the testing compositions.
        """
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = test_json['configurations']
        comp = {'comp': test_json['compositions']}
        _id = ObjectId()
        token = 'ThisIsATestToken'

        with current_app.test_client() as client:
            sess_res = client.post(
                '/session',
                data=json.dumps(
                    {
                        '_id': str(_id),
                        'token': str(token),
                        'last_configurations': configs,
                        'last_compositions': comp
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(sess_res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_res.status_code == 201)

            # We need to update Ae1 and Ae3 first before we can properly get
            # the results for Xfe
            res = client.post(
                '/configs/auto/ae',
                data=json.dumps(
                    {
                        'auto_calculate_ae': True,
                        'compositions': comp
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(res.status_code == 200)

            # Now we can test Xfe
            res = client.post(
                '/configs/auto/xfe',
                data=json.dumps(
                    {
                        'auto_calculate_xfe': True,
                        'compositions': comp
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_xfe'])
            xfe = np.float64(data['data']['xfe_value'])
            cf = np.float64(data['data']['cf_value'])
            ceut = np.float64(data['data']['ceut_value'])
            self.assertAlmostEqual(cf, 0.012, 3)
            self.assertAlmostEqual(sess_store['cf_value'], 0.012, 3)
            self.assertAlmostEqual(ceut, 0.8300, 4)
            self.assertAlmostEqual(sess_store['ceut_value'], 0.8300, 4)
            self.assertAlmostEqual(xfe, 0.94621026894865523, 8)
            self.assertAlmostEqual(sess_store['xfe_value'], 0.94621026895, 8)


if __name__ == '__main__':
    unittest.main()
