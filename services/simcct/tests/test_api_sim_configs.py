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

from sim_app.app import BASE_DIR
from tests.test_api_base import BaseTestCase
from sim_app.schemas import AlloySchema, ConfigurationsSchema

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSimConfigurations(BaseTestCase):

    # NOTE:
    #  - We can treat the session stores of the compositions and configurations
    #    as always being the one that's displayed on the Client UI.

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

    def test_on_compositions_change(self):
        """Ensure if we update the compositions it changes in session store."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            new_comp = comp
            new_comp['alloy']['compositions'][0]['weight'] = 0.050

            res = client.post(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Compositions updated.')
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            session_comp = session.get(f'{token}:alloy')
            self.assertEqual(session_comp, new_comp['alloy'])

    def test_on_comp_change_invalid_comp_schema(self):
        """Ensure if we send a bad alloy schema we get errors."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            new_comp = {
                    'alloy': {'name': 'Bad_Alloy', 'compositions': 'hello'},
                    'alloy_type': 'parent'
            }

            res = client.post(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'],
                             'Alloy failed schema validation.')
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            self.assertTrue(data['errors'])
            session_comp = session.get(f'{token}:alloy')
            self.assertNotEqual(session_comp, new_comp)

    def test_on_comp_change_auto_update_temps(self):
        """Ensure if we update compositions schema we also auto update."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            # We need to make auto_calculate true by using the endpoints
            client.post(
                '/configs/auto/ms-bs',
                data=json.dumps(
                    {
                        'auto_calculate_ms_bs': True,
                        'transformation_method': 'Li98'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            client.post(
                '/configs/auto/ae',
                data=json.dumps({'auto_calculate_ae': True}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            client.post(
                '/configs/auto/xfe',
                data=json.dumps({'auto_calculate_xfe': True}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            sess_store = session.get(f'{token}:configurations')
            self.assertAlmostEqual(sess_store['ms_temp'], 464.1960, 4)
            self.assertAlmostEqual(sess_store['bs_temp'], 563.2380, 4)
            self.assertAlmostEqual(sess_store['ae1_temp'], 700.90196, 4)
            self.assertAlmostEqual(sess_store['ae3_temp'], 845.83796, 4)
            self.assertAlmostEqual(sess_store['cf_value'], 0.012, 3)
            self.assertAlmostEqual(sess_store['ceut_value'], 0.8300, 4)
            self.assertAlmostEqual(sess_store['xfe_value'], 0.9462, 4)

            # Now we change the compositions and make sure it's all updated
            # with the composition change
            new_comp = comp
            new_comp['alloy']['compositions'][0]['weight'] = 0.050
            new_comp['alloy']['compositions'][1]['weight'] = 1.6

            res = client.post(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'Compositions and other values updated.'
            )
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])

            # ANSTO SimCCT results
            ms_temp = 465.6100
            bs_temp = 567.44
            ae1_temp = 702.7388
            ae3_temp = 847.10445
            ceut_value = 0.8300
            xfe_value = 0.93888

            self.assertAlmostEqual(data['data']['ms_temp'], ms_temp, 4)
            self.assertAlmostEqual(data['data']['bs_temp'], bs_temp, 2)
            self.assertAlmostEqual(data['data']['ae1_temp'], ae1_temp, 4)
            self.assertAlmostEqual(data['data']['ae3_temp'], ae3_temp, 4)
            self.assertAlmostEqual(data['data']['cf_value'], 0.012, 3)
            self.assertAlmostEqual(data['data']['ceut_value'], ceut_value, 4)
            self.assertAlmostEqual(data['data']['xfe_value'], xfe_value, 4)
            sess_store = session.get(f'{token}:configurations')
            self.assertAlmostEqual(sess_store['ms_temp'], ms_temp, 4)
            self.assertAlmostEqual(sess_store['bs_temp'], bs_temp, 2)
            self.assertAlmostEqual(sess_store['ae1_temp'], ae1_temp, 4)
            self.assertAlmostEqual(sess_store['ae3_temp'], ae3_temp, 4)
            self.assertAlmostEqual(sess_store['cf_value'], 0.012, 3)
            self.assertAlmostEqual(sess_store['ceut_value'], ceut_value, 4)
            self.assertAlmostEqual(sess_store['xfe_value'], xfe_value, 4)

    def test_on_method_change(self):
        """Ensure we can change the method in the session store."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            method = 'Kirkaldy83'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            session_store = session.get(f'{token}:configurations')
            self.assertEqual(data['message'], f'Changed to {method} method.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertEqual(session_store['method'], 'Kirkaldy83')

            method = 'Li98'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            session_store = session.get(f'{token}:configurations')
            self.assertEqual(data['message'], f'Changed to {method} method.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertEqual(session_store['method'], method)

    def test_auto_update_ms_bs(self):
        """Ensure we get the correct calculations for MS and BS given the
        testing configs and the testing compositions.
        """
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.post(
                '/configs/auto/ms-bs',
                data=json.dumps(
                    {
                        'auto_calculate_ms_bs': True,
                        'transformation_method': 'Li98'
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
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.post(
                '/configs/auto/ae',
                data=json.dumps({'auto_calculate_ae': True}),
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
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

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
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            # We need to update Ae1 and Ae3 first before we can properly get
            # the results for Xfe
            res = client.post(
                '/configs/auto/ae',
                data=json.dumps({'auto_calculate_ae': True}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(res.status_code == 200)

            # Now we can test Xfe
            res = client.post(
                '/configs/auto/xfe',
                data=json.dumps({'auto_calculate_xfe': True}),
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

    def test_configurations_no_auth_header(self):
        """Ensure it fails with no header."""
        with current_app.test_client() as client:
            method = 'Kirkaldy83'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert401(res)
            self.assertEqual(
                data['message'], 'No valid Authorization in header.'
            )
            self.assertEqual(data['status'], 'fail')

    def test_configurations_bad_auth_header(self):
        """Ensure it fails with a bad header."""
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            method = 'Kirkaldy83'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                headers={'Authorization': 'Bearer '},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert401(res)
            self.assertEqual(data['message'], 'Invalid JWT token in header.')
            self.assertEqual(data['status'], 'fail')

    def test_configurations_empty_payload(self):
        """Ensure you miss 100% of the shots you don't take."""
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.post(
                '/configs/comp/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.post(
                '/configs/auto/ms-bs',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.post(
                '/configs/auto/ae',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.post(
                '/configs/auto/xfe',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_no_method_payload(self):
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': ''}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'No method was provided.')
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_incorrect_method_payload(self):
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': 'AndrewMethod!'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(
                data['message'],
                'Invalid method provided (must be Li98 or Kirkaldy83).'
            )
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_empty_session_store(self):
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.post(
                '/configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEqual(
                data['message'], 'No previous session configurations was set.'
            )
            self.assertEqual(data['status'], 'fail')

    def test_on_comp_change_bad_comp_payload(self):
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            prev_sess_comp = session.get(f'{token}:alloy')
            res = client.post(
                '/configs/comp/update',
                data=json.dumps({'compositions': []}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'No composition list was provided.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            after_sess_comp = session.get(f'{token}:alloy')
            self.assertEqual(prev_sess_comp, after_sess_comp)

    def test_on_comp_change_no_ae_check(self):
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            # We need to make auto_calculate true by using the endpoints
            client.post(
                '/configs/auto/ms-bs',
                data=json.dumps(
                    {
                        'auto_calculate_ms_bs': True,
                        'transformation_method': 'Kirkaldy83'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            client.post(
                '/configs/auto/xfe',
                data=json.dumps({'auto_calculate_xfe': True}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            session[f'{token}:configurations']['auto_calculate_xfe'] = True

            sess_store = session.get(f'{token}:configurations')
            self.assertTrue(sess_store['auto_calculate_xfe'])
            self.assertTrue(sess_store['auto_calculate_ms_bs'])
            self.assertFalse(sess_store['auto_calculate_ae'])
            self.assertAlmostEqual(sess_store['ms_temp'], 477.59400, 4)
            self.assertAlmostEqual(sess_store['bs_temp'], 582.2380, 4)
            self.assertEqual(sess_store['ae1_temp'], 0.0)
            self.assertEqual(sess_store['ae3_temp'], 0.0)

            # Now we change the compositions and make sure it's all updated
            # with the composition change
            new_comp = comp
            alloy_comp = new_comp['alloy']
            alloy_comp['compositions'][0]['weight'] = 0.050
            alloy_comp['compositions'][1]['weight'] = 0.3
            alloy_comp['compositions'][2]['weight'] = 1.6

            res = client.post(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session.get(f'{token}:configurations')

            self.assertTrue(sess_store['auto_calculate_xfe'])
            self.assertEqual(
                data['message'], (
                    'Ae1 must be more than zero to find the '
                    'Equilibrium Phase Fraction.'
                )
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            self.assertTrue(data['data'])

    def test_on_comp_change_only_auto_ms_bs(self):
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            # We need to make auto_calculate true by using the endpoints
            client.post(
                '/configs/auto/ae',
                data=json.dumps({'auto_calculate_ae': True}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            sess_store = session.get(f'{token}:configurations')
            self.assertFalse(sess_store['auto_calculate_xfe'])
            self.assertTrue(sess_store['auto_calculate_ae'])
            self.assertFalse(sess_store['auto_calculate_ms_bs'])

            # Now we change the compositions and make sure it's all updated
            # with the composition change
            new_comp = comp
            new_comp['alloy']['compositions'][0]['weight'] = 0.05
            new_comp['alloy']['compositions'][1]['weight'] = 1.6

            res = client.post(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session.get(f'{token}:configurations')

            self.assertEqual(
                data['message'], 'Compositions and other values updated.'
            )
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            self.assertAlmostEqual(sess_store['ae1_temp'], 702.7388, 4)
            self.assertAlmostEqual(sess_store['ae3_temp'], 847.10445, 4)
            with self.assertRaises(KeyError):
                self.assertFalse(data['data']['ms_temp'])
                self.assertFalse(data['data']['bs_temp'])

    def test_auto_update_ms_bs_no_method_provided(self):
        """Ensure we get the correct calculations for MS and BS given the
        testing configs and the testing compositions.
        """
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.post(
                '/configs/auto/ms-bs',
                data=json.dumps(
                    {
                        'auto_calculate_ms_bs': True,
                        'transformation_method': ''
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assertEqual(
                data['message'], 'You must provide a transformation method.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            self.assertFalse(sess_store['auto_calculate_ms_bs'])

    def test_auto_update_ms_bs_kirkaldy_method(self):
        """Ensure we get the correct calculations for MS and BS given Kirkaldy83
        method testing configs and the testing compositions.
        """
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.post(
                '/configs/auto/ms-bs',
                data=json.dumps(
                    {
                        'auto_calculate_ms_bs': True,
                        'transformation_method': 'Kirkaldy83'
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
            self.assertAlmostEqual(sess_store['ms_temp'], 477.5940, 4)
            self.assertAlmostEqual(sess_store['bs_temp'], 582.2380, 3)
            self.assertAlmostEqual(ms_temp, 477.5940, 4)
            self.assertAlmostEqual(bs_temp, 582.2380, 4)

    def test_auto_update_bad_json_false(self):
        """Testing sending False for auto calculate."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            res = client.post(
                '/configs/auto/ms-bs',
                data=json.dumps({
                    'auto_calculate_ms_bs': False,
                }),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert400(res)
            self.assertEqual(
                data['message'],
                'Post data auto calculate for MS or BS is false.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertFalse(sess_store['auto_calculate_ms_bs'])

            res = client.post(
                '/configs/auto/ae',
                data=json.dumps({
                    'auto_calculate_ae': False,
                }),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert400(res)
            self.assertEqual(
                data['message'], 'Auto calculate for Austenite is false.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertFalse(sess_store['auto_calculate_ae'])

            res = client.post(
                '/configs/auto/xfe',
                data=json.dumps({
                    'auto_calculate_xfe': False,
                }),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert400(res)
            self.assertEqual(
                data['message'],
                'Auto calculate for Equilibrium Phase is false.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertFalse(sess_store['auto_calculate_xfe'])

    def test_on_configs_change(self):
        """Ensure that if we send new configurations we store it in session."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            # Since login stores the configs already, we need to make some
            # changes to see if it updates.
            configs['start_temp'] = 901

            res = client.put(
                '/configs/update',
                data=json.dumps(configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 204)
            self.assertFalse(res.data)
            session_store = session.get(f'{token}:configurations')
            self.assertEqual(configs, session_store)

    def test_on_configs_change_empty_json(self):
        """Ensure that if we send an empty JSON we get an error."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            res = client.put(
                '/configs/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_on_configs_change_before_login(self):
        """Ensure if the user has not logged in, they have no previous store."""
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = test_json['configurations']
        token = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123'
        configs.pop('nucleation_start')
        configs.pop('nucleation_finish')

        with current_app.test_client() as client:
            res = client.put(
                '/configs/update',
                data=json.dumps(configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assert404(res)
            # TODO: CURRENTLY HERE


if __name__ == '__main__':
    unittest.main()
