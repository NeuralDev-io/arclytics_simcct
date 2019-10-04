# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_sessions.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.10.03'

import json
import os
import unittest

from mongoengine import get_db

from sim_api.models import User
from sim_api.extensions.SimSession import SimSessionService
from tests.test_api_base import BaseTestCase
from tests.test_utilities import test_login

class TestSimSessionsService(BaseTestCase):
    """Tests for the Sim Session endpoints"""

    def tearDown(self) -> None:
        db = get_db('default')
        self.assertTrue(db.name, 'arc_test')
        db.users.drop()
        db.feedback.drop()

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def test_put_sim_sesion_empty_request(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.put(
                '/api/v1/sim/session/update',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_put_sim_session_no_configuration(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.put(
                '/api/v1/sim/session/update',
                data=json.dumps({
                    'alloy_store': 'something'
                }),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No configuration provided.')

    def test_put_sim_session_invalid_configuration(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.put(
                '/api/v1/sim/session/update',
                data=json.dumps({
                    'configuration': 21
                }),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Configuration must be of type dict.'
            )

    def test_put_sim_session_no_alloy_store(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.put(
                '/api/v1/sim/session/update',
                data=json.dumps({
                    'configuration': {
                        'some_key': 'some_value'
                    }
                }),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'No alloy store provided.'
            )

    def test_put_sim_session_invalid_alloy_store(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.put(
                '/api/v1/sim/session/update',
                data=json.dumps({
                    'configuration': {
                        'some_key': 'some_value'
                    },
                    'alloy_store': 21
                }),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Alloy store must be of type dict.'
            )

    def test_put_sim_session_success(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.put(
                '/api/v1/sim/session/update',
                data=json.dumps({
                    'configuration': {
                        'some_key': 'some_value'
                    },
                    'alloy_store': {
                        'some_key': 'some_value'
                    }
                }),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], 'Session updated.'
            )

    def test_reset_sim_session_success(self):
        cal = User(
            **{
                'email': 'calkestis@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('dontstandout')
        cal.save()

        with self.client as client:
            test_login(client, cal.email, 'dontstandout')

            resp = client.delete(
                '/api/v1/sim/session/reset',
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], 'Session cleared.'
            )

            session_store = SimSessionService().load_session()
            self.assertEqual(session_store['configuration'], None)
            self.assertEqual(session_store['alloy_store'], None)
            self.assertEqual(session_store['simulation_results'], None)

if __name__ == '__main__':
    unittest.main()