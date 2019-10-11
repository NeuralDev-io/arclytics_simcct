# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_share.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.07.03'

import json
import os
import unittest
from copy import deepcopy
from pathlib import Path

from mongoengine import get_db

from arc_logging import AppLogger
from sim_api.models import SharedSimulation, User
from sim_api.token import (generate_shared_simulation_token, generate_url)
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

logger = AppLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'share_sim_data.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    _TEST_JSON = json.load(f)

CONFIGS = _TEST_JSON['configurations']
ALLOY_STORE = _TEST_JSON['alloy_store']
SIMULATION_RESULTS = _TEST_JSON['simulation_results']


class TestShareService(BaseTestCase):
    """Test for sharing simulations via link and email"""
    def setUp(self) -> None:
        assert app.config['TESTING'] is True
        self.mongo = get_db('default')

    def tearDown(self) -> None:
        db = get_db('default')
        self.assertTrue(db.name, 'arc_test')
        db.users.drop()
        SharedSimulation.objects.delete()

    @classmethod
    def tearDownClass(cls) -> None:
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()
        SharedSimulation.objects.delete()

    #
    # @staticmethod
    # def login(
    #         client, email='luke@skywalker.io', password='IronHeart!'
    # ):
    #     client.post(
    #         '/v1/sim/auth/login',
    #         data=json.dumps({
    #             'email': email,
    #             'password': password
    #         }),
    #         content_type='application/json'
    #     )
    #     test_login(client, email, password)
    #     return email

    def test_share_configuration_link_success(self):
        """
        Ensure a user is able to obtain a shareable link for valid simulation
        data.
        """

        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = self.client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(resp.status_code, 201)
            shared_simulation = SharedSimulation.objects.get(
                owner_email='luke@arclytics.io'
            )
            sim_token = generate_shared_simulation_token(
                str(shared_simulation.id)
            )
            sim_url = generate_url(
                'share.request_shared_simulation', sim_token
            )
            self.assertEqual(data['link'], sim_url)

    def test_share_configuration_link_no_data(self):
        """
        Ensure a share via link request with no simulation data fails.
        """

        luke = User(
            **{
                'email': 'luke@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_share_configuration_link_invalid_element_symbol(self):
        """
        Ensure a share via link request with an invalid element symbol fails.
        """

        luke = User(
            **{
                'email': 'luke@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        alloy_store = deepcopy(ALLOY_STORE)
        # invalid element symbol
        alloy_store['alloys']['parent']['compositions'].append(
            {
                'symbol': 'DM',
                'weight': 4.003
            }
        )

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Element Symbol Invalid.')

    def test_share_configuration_link_invalid_element(self):
        """
        Ensure a share via link request with an invalid element fails.
        """

        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        alloy_store = deepcopy(ALLOY_STORE)
        # invalid element, no symbol
        alloy_store['alloys']['parent']['compositions'].append(
            {'weight': 4.003}
        )

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Element Invalid.')

    def test_share_configuration_link_missing_elements(self):
        """
        Ensure a share via link request that is missing essential elements (C,
        Mn, Ni, Cr, Mo, Si, Co, W, As, Fe, B, C) in alloys fails.
        """

        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        alloy_store = deepcopy(ALLOY_STORE)
        del alloy_store['alloys']['parent']['compositions'][0]
        del alloy_store['alloys']['weld']['compositions'][0]
        del alloy_store['alloys']['mix']['compositions'][0]

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Alloy is missing essential elements.'
            )

    def test_share_configuration_link_duplicate_element(self):
        """
        Ensure a share request that contains an alloy with a duplicate element
        fails.
        """

        luke = User(
            **{
                'email': 'lake@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        alloy_store = deepcopy(ALLOY_STORE)
        alloy_store['alloys']['parent']['compositions'].append(
            {
                'symbol': 'C',
                'weight': 12.02
            }
        )

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': alloy_store,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Alloy contains duplicate elements.'
            )

    def test_share_configuration_link_validation_error(self):
        """
        Ensure a share via link request with invalid simulation information
        (e.g. missing alloy_store information) fails.
        """

        luke = User(
            **{
                'email': 'luko@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': {
                            'alloy_option': 'single'
                        },
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Validation error.')

    # def test_share_configuration_single_email_success(self):
    #     """
    #     Ensure a user is able to obtain a share simulation data via a link sent
    #     in an email to an address of their choice.
    #
    #     This test requires a real email address in order to ensure that the
    #     email has been sent.
    #     """
    #
    #     luke = User(
    #         **{
    #             'email': 'luke@arclytics.com',
    #             'first_name': 'Luke',
    #             'last_name': 'Skywalker'
    #         }
    #     )
    #     luke.set_password('NeverJoinYou')
    #     luke.verified = True
    #     luke.save()
    #
    #     with self.client as client:
    #         test_login(client, luke.email, 'NeverJoinYou')
    #         resp = client.post(
    #             '/v1/sim/user/share/simulation/email',
    #             data=json.dumps(
    #                 {
    #                     # 'emails': ['davidmatthews1004@gmail.com'],
    #                     'emails': ['davidtest@arclytics.com'],
    #                     'configurations': CONFIGS,
    #                     'alloy_store': ALLOY_STORE,
    #                     'simulation_results': SIMULATION_RESULTS
    #                 }
    #             ),
    #
    #             content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(data['message'], 'Email(s) sent.')
    #         self.assertEqual(data['status'], 'success')
    #         self.assertEqual(resp.status_code, 201)
    #         shared_simulation = SharedSimulation.objects.get(
    #             owner_email=luke.email
    #         )
    #         sim_token = generate_shared_simulation_token(
    #             str(shared_simulation.id)
    #         )
    #         sim_url = generate_url(
    #             'share.request_shared_simulation', sim_token
    #         )
    #         self.assertEqual(data['link'], sim_url)

    # def test_share_configuration_multiple_emails_success(self):
    #     """
    #     Ensure a user is able to obtain a share simulation data via a link sent
    #     in emails to addresses of their choice.
    #
    #     This test requires real email addresses in order to ensure that the
    #     emails have been sent.
    #     """
    #
    #     luke = User(
    #         **{
    #             'email': 'skywalkerl@arclytics.com',
    #             'first_name': 'Luke',
    #             'last_name': 'Skywalker'
    #         }
    #     )
    #     luke.set_password('NeverJoinYou')
    #     luke.verified = True
    #     luke.save()
    #
    #     with self.client as client:
    #         test_login(client, luke.email, 'NeverJoinYou')
    #         resp = client.post(
    #             '/v1/sim/user/share/simulation/email',
    #             data=json.dumps(
    #                 {
    #                     # 'emails': ['davidmatthews1004@gmail.com'],
    #                     'emails': [
    #                         'davidtest@arclytics.com',
    #                         'davidtest2@arclytics.com'
    #                     ],
    #                     'configurations': CONFIGS,
    #                     'alloy_store': ALLOY_STORE,
    #                     'simulation_results': SIMULATION_RESULTS
    #                 }
    #             ),
    #
    #             content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(data['message'], 'Email(s) sent.')
    #         self.assertEqual(data['status'], 'success')
    #         self.assertEqual(resp.status_code, 201)
    #         shared_simulation = SharedSimulation.objects.get(
    #             owner_email=luke.email
    #         )
    #         sim_token = generate_shared_simulation_token(
    #             str(shared_simulation.id)
    #         )
    #         sim_url = generate_url(
    #             'share.request_shared_simulation', sim_token
    #         )
    #         self.assertEqual(data['link'], sim_url)

    def test_share_configuration_email_no_email(self):
        """
        Ensure a share via email request with no email address provided fails.
        """

        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/email',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No email addresses provided.')

    def test_share_configuration_email_invalid_email_type(self):
        """
        Ensure a share via email request with an invalid email type in the
        request body fails.
        """

        luke = User(
            **{
                'email': 'lukek@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/email',
                data=json.dumps(
                    {
                        'emails': [1234],
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(
                data['message'], 'An email address is invalid in the list.'
            )
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')

    def test_share_configuration_email_invalid_email(self):
        """
        Ensure a share via email request with one invalid email address (e.g.
        invalidemail@com) and no other addresses fails.
        """

        luke = User(
            **{
                'email': 'luake@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/email',
                data=json.dumps(
                    {
                        'emails': ['invalidemail@com'],
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_share_configuration_email_invalid_email_in_list(self):
        """
        Ensure a share via email request with one invalid email address (e.g.
        invalidemail@com) in a list of email addresses fails.
        """

        luke = User(
            **{
                'email': 'lukge@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.post(
                '/v1/sim/user/share/simulation/email',
                data=json.dumps(
                    {
                        'emails':
                        ['invalidemail@com', 'brickmatic479@gmail.com'],
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_request_shared_simulation(self):
        """
        Ensure that when a link to a shared simulation link is clicked on, the
        client is redirected successfully.
        """

        luke = User(
            **{
                'email': 'luke@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp_create_link = self.client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )
            data_1 = json.loads(resp_create_link.data.decode())
            self.assertEqual(resp_create_link.status_code, 201)
            self.assertEqual(data_1['status'], 'success')

            link = data_1['link']

            resp_request_simulation = self.client.get(
                link, content_type='application/json'
            )
            self.assertEquals(resp_request_simulation.status_code, 302)
            token = resp_request_simulation.headers['Location'].split('/')[-1]
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = (
                f'{protocol}://{client_host}:{client_port}/share/simulation/'
                f'{token}'
            )
            self.assertRedirects(resp_request_simulation, redirect_url)

    def test_view_shared_simulation(self):
        """
        Ensure shared simulation data can be viewed via a generated link.
        """

        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp_create = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            shared_simulation = SharedSimulation.objects.get(
                owner_email=luke.email
            )
            sim_token = generate_shared_simulation_token(
                str(shared_simulation.id)
            )
            sim_view_url = generate_url(
                'share.view_shared_simulation', sim_token
            )

            resp_view = client.get(
                sim_view_url, content_type='application/json'
            )

            data = json.loads(resp_view.data.decode())
            self.assertEqual(resp_view.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['owner_email'], luke.email)
            self.assertEqual(data['data']['configurations']['ms_temp'], 0.2)
            self.assertEqual(
                data['data']['alloy_store']['alloy_option'], 'single'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['parent']['compositions']
                [2]['symbol'], 'Ni'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['parent']['compositions']
                [5]['weight'], 28.09
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['weld']['name'],
                'Weld Name'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['weld']['compositions']
                [1]['weight'], 54.94
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['weld']['compositions']
                [8]['symbol'], 'As'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['mix']['compositions'][0]
                ['symbol'], 'C'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['mix']['compositions']
                [11]['weight'], 14.01
            )

    def test_view_shared_simulation_invalid_token(self):
        """
        Ensure a view shared simulation request with an invalid simulation token
        fails.
        """
        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        bad_token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        url = generate_url('share.view_shared_simulation', bad_token)

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid token.')

    def test_view_shared_simulation_dne(self):
        """
        Ensure a view shared simulation request on a simulation that does not
        exist at the time of the request fails.
        """

        luke = User(
            **{
                'email': 'luooke@skywalker.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        with self.client as client:
            test_login(client, luke.email, 'NeverJoinYou')
            resp_create = client.post(
                '/v1/sim/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configurations': CONFIGS,
                        'alloy_store': ALLOY_STORE,
                        'simulation_results': SIMULATION_RESULTS
                    }
                ),
                content_type='application/json'
            )

            shared_sim = SharedSimulation.objects.get(owner_email=luke.email)
            sim_token = generate_shared_simulation_token(str(shared_sim.id))
            sim_url = generate_url('share.view_shared_simulation', sim_token)
            shared_sim.delete()
            resp_view = client.get(sim_url, content_type='application/json')

            data = json.loads(resp_view.data.decode())
            self.assertEqual(resp_view.status_code, 404)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Simulation does not exist.')


if __name__ == '__main__':
    unittest.main()
