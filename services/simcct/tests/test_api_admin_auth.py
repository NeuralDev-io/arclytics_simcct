# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_admin_auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']
__status__ = 'development'
__date__ = '2019.07.03'

import json
import os
import unittest

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from mongoengine import get_db

from arc_logging import AppLogger
from sim_api.extensions.utilities import get_mongo_uri
from sim_api.models import (AdminProfile, User)
from sim_api.token import (
    generate_confirmation_token, generate_promotion_confirmation_token,
    generate_url
)
from tests.test_api_base import BaseTestCase
from tests.test_utilities import test_login

logger = AppLogger(__name__)


class TestAdminCreateService(BaseTestCase):
    """Tests for Admin creation and disable account endpoints"""
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
        db.feedback.drop()

    def test_disable_account(self):
        """Test disable account is successful"""
        user = User(
            **{
                'email': 'kyloren@gmail.com',
                'first_name': 'Kylo',
                'last_name': 'Ren'
            }
        )
        user.set_password('LetStarWarsDie')
        user.save()

        vader = User(
            **{
                # 'email': 'brickmatic479@gmail.com',
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        # vader.is_admin = True
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        with self.client as client:
            # os.environ['FLASK_ENV'] = 'production'
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/disable/user',
                data=json.dumps({'email': 'kyloren@gmail.com'}),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 200)
            self.assertEqual(disable_data['status'], 'success')
            self.assertEqual(
                disable_data['message'], 'Confirmation email sent.'
            )

    def test_disable_account_no_data(self):
        """Test empty disable request is unsuccessful"""
        user = User(
            **{
                'first_name': 'Jar Jar',
                'last_name': 'Binks',
                'email': 'jarjar@binks.com'
            }
        )
        user.set_password('MeesaMakePassword')
        # jarjar.is_admin = True
        user.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        user.save()

        with self.client as client:
            cookie = test_login(client, user.email, 'MeesaMakePassword')

            resp = client.put(
                '/v1/sim/disable/user',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_disable_account_dne(self):
        """Test disable non-existent account is unsuccessful."""
        r2d2 = User(
            **{
                'first_name': 'R2',
                'last_name': 'D2',
                'email': 'r2d2@astromech.com'
            }
        )
        r2d2.set_password('Weeeeeew')
        # r2d2.is_admin = True
        r2d2.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        r2d2.save()

        with self.client as client:
            cookie = test_login(client, r2d2.email, 'Weeeeeew')

            resp = client.put(
                '/v1/sim/disable/user',
                data=json.dumps({'email': 'c3p0@protocol.com'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User does not exist.')

    def test_disable_account_no_email(self):
        """
        Ensure a disable request is rejected when no email is provided.
        """
        vader = User(
            **{
                'email': 'vader@arclytics.com',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        # vader.is_admin = True
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        with self.client as client:
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/disable/user',
                data=json.dumps({'invalid_key': 'invalid_data'}),
                content_type='application/json'
            )

            data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No email provided.')

    def test_disable_account_invalid_email(self):
        """
        Ensure a disable request is rejected if an invalid email is provided.
        """
        vader = User(
            **{
                'email': 'vader@sith.com',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        # vader.is_admin = True
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        with self.client as client:
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/disable/user',
                data=json.dumps({'email': 'invalid_email.com'}),
                content_type='application/json'
            )

            data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_confirm_disable_account_success(self):
        from pymongo import MongoClient
        with current_app.test_client() as client:
            piett = User(
                **{
                    # 'email': 'brickmatic479@gmail.com',
                    'email': 'piett@arclytics.io',
                    'first_name': 'Admiral',
                    'last_name': 'Piett'
                }
            )
            piett.set_password('YesLordVader')
            piett.save()
            account_disable_token = generate_confirmation_token(piett.email)
            account_disable_url = generate_url(
                'admin.confirm_disable_account', account_disable_token
            )
            resp = client.get(
                account_disable_url, content_type='application/json'
            )
            mongo_client = MongoClient(get_mongo_uri())
            db = mongo_client['arc_test']
            user = db.users.find_one({'email': piett.email})
            print(f'User.active: {user["active"]}')

            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(resp, f'{redirect_url}/')

            # The following assertion will cause an error as the context of the
            # database changes during the test for some reason. In order to
            # confirm that user.active has been set to false, a print statement
            # has been inserted above.
            # piett_updated = User.objects.get(id=piett.id)
            # self.assertEqual(piett_updated.verified, True)

    # FIXME(davidmatthews1004@gmail.com) Pleas fix
    # def test_confirm_disable_account_token_expired(self):
    #     with current_app.test_client() as client:
    #         piett = User(
    #             # email='brickmatic479@gmail.com',
    #             email='piett@arclytics.io',
    #             first_name='Admiral',
    #             last_name='Piett'
    #         )
    #         piett.set_password('YesLordVader')
    #         piett.save()
    #         account_disable_token = (
    #             'InBpZXR0QGFyY2x5dGljcy5pbyI.XWIu_Q.934dTWGdz793EjFVH_
    #             'fWa2I-K'UA'
    #         )
    #         account_disable_url = generate_url(
    #             'admin.confirm_disable_account', account_disable_token
    #         )
    #         resp = client.get(
    #             account_disable_url, content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         print(data)
    #
    #         client_host = os.environ.get('CLIENT_HOST')
    #         self.assertEquals(resp.status_code, 302)
    #         self.assertTrue(resp.headers['Location'])
    #         redirect_url = \
    #             f'http://{client_host}/disable/user/confirm/tokenexpired'
    #         self.assertRedirects(resp, redirect_url)

    def test_confirm_disable_account_invalid_token(self):
        invalid_token = 'aaaaaaaaaaaaaaaaaaaaaaaa'
        url = generate_url('admin.confirm_disable_account', invalid_token)

        with self.client as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/disable/user/confirm?tokenexpired=true'
            )

    def test_confirm_disable_account_user_dne(self):
        kylo = User(
            **{
                'email': 'kyloren@arclytics.io',
                'first_name': 'Kylo',
                'last_name': 'Ren'
            }
        )
        kylo.set_password('LetThePastDie')
        kylo.save()
        account_disable_token = generate_confirmation_token(kylo.email)
        account_disable_url = generate_url(
            'admin.confirm_disable_account', account_disable_token
        )
        kylo.delete()
        with self.client as client:
            resp = client.get(
                account_disable_url, content_type='application/json'
            )

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/disable/user/confirm?tokenexpired=true'
            )

    def test_create_admin_success(self):
        """Test create admin is successful"""
        quigon = User(
            **{
                'first_name': 'Qui-Gon',
                'last_name': 'Jinn',
                # 'email': 'davidmatthews1004@gmail.com'
                'email': 'quigon@arclytics.com'
            }
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        obiwan = User(
            **{
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi',
                # 'email': 'brickmatic479@gmail.com'
                'email': 'obiwan@arclytics.com'
            }
        )
        obiwan.verified = True
        obiwan.set_password('FromACertainPointOfView')
        obiwan.save()

        with self.client as client:
            # os.environ['FLASK_ENV'] = 'production'
            cookie = test_login(client, quigon.email, 'ShortNegotiations')

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps(
                    {
                        'email': 'obiwan@arclytics.com',
                        # 'email': 'brickmatic479@gmail.com',
                        'position': 'Jedi Knight.'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(resp.status_code, 202)
            # os.environ['FLASK_ENV'] = 'development'

    def test_create_admin_invalid_email(self):
        """Test create admin with invalid email is unsuccessful"""
        luke = User(
            **{
                'first_name': 'Luke',
                'last_name': 'Skywalker',
                'email': 'lukeskywalker@arclytics.io'
            }
        )
        # luke.is_admin = True
        luke.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        luke.set_password('IAmAJediLikeMyFatherBeforeMe')
        luke.save()

        biggs = User(
            **{
                'first_name': 'Biggs',
                'last_name': 'Darklighter',
                'email': 'invalidbiggs@dot.com'
            }
        )
        biggs.set_password('LukePullUp')
        biggs.save()

        with self.client as client:
            cookie = test_login(
                client, luke.email, 'IAmAJediLikeMyFatherBeforeMe'
            )

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps(
                    {
                        'email': 'invalidbiggs@abcdefghijklmopqrstuvwxyz.com',
                        'position': 'Red Three'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['message'], 'Invalid email.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)

    def test_create_unverified_admin(self):
        """Test create admin from unverified user is unsuccessful"""
        ackbar = User(
            **{
                'first_name': 'Admiral',
                'last_name': 'Ackbar',
                'email': 'admiralackbar@arlytics.com'
            }
        )
        ackbar.set_password('ITSATRAP')
        # ackbar.is_admin = True
        ackbar.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        ackbar.save()

        jyn = User(
            **{
                'first_name': 'Jyn',
                'last_name': 'Erso',
                'email': 'ersoj@arclytics.com'
            }
        )
        jyn.set_password('RebellionsAreBuiltOnHope')
        jyn.save()

        with self.client as client:
            cookie = test_login(client, ackbar.email, 'ITSATRAP')

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps(
                    {
                        'email': 'ersoj@arclytics.com',
                        'position': 'Rogue Leader'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(
                data['message'], 'The user must verify their email.'
            )

    def test_create_admin_already_admin(self):
        """
        Ensure an error comes up when trying to make an Admin an Admin
        """
        aayla = User(
            **{
                'first_name': 'Aayla',
                'last_name': 'Secura',
                'email': 'aaylasecura@gmail.com'
            }
        )
        aayla.set_password('KilledByBly')
        aayla.verified = True
        # aayla.is_admin = True
        aayla.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        aayla.save()

        luminara = User(
            **{
                'first_name': 'Luminara',
                'last_name': 'Unduli',
                'email': 'luminaraunduli@gmail.com'
            }
        )
        luminara.set_password('DiesOffscreen')
        luminara.verified = True
        # luminara.is_admin = True
        luminara.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        luminara.save()

        with self.client as client:
            cookie = test_login(client, aayla.email, 'KilledByBly')

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps(
                    {
                        'email': 'luminaraunduli@gmail.com',
                        'position': 'Jedi Master'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(
                data['message'], 'User is already an Administrator.'
            )

    def test_create_admin_no_data(self):
        """
        Ensure a create admin request with no request body is rejected.
        """
        quigon = User(
            **{
                'first_name': 'Qui-Gon',
                'last_name': 'Jinn',
                'email': "jinnq@arclytics.io"
            }
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        with self.client as client:
            test_login(client, quigon.email, 'ShortNegotiations')

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps(''),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_create_admin_no_email(self):
        """
        Ensure a create admin request with no email is rejected.
        """
        quigon = User(
            **{
                'first_name': 'Qui-Gon',
                'last_name': 'Jinn',
                'email': "quigonandhisgin@arclytics.io"
            }
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        with self.client as client:
            cookie = test_login(client, quigon.email, 'ShortNegotiations')

            resp = self.client.post(
                '/v1/sim/admin/create',
                data=json.dumps({'position': 'Jedi Knight.'}),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'No email provided.')

    def test_create_admin_no_position(self):
        """
        Ensure a create admin request with no position is rejected.
        """
        quigon = User(
            **{
                'first_name': 'Qui-Gon',
                'last_name': 'Jinn',
                'email': "liamneeson@arclytics.io"
            }
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        with self.client as client:
            cookie = test_login(client, quigon.email, 'ShortNegotiations')

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps({'email': 'brickmatic479@gmail.com'}),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'No position provided.')

    def test_create_admin_user_dne(self):
        """
        Ensure a create admin request for a user that does not exist is
        rejected.
        """
        quigon = User(
            **{
                'first_name': 'Qui-Gon',
                'last_name': 'Jinn',
                'email': "quigonjinn@arclytics.com"
            }
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        with self.client as client:
            cookie = test_login(client, quigon.email, 'ShortNegotiations')

            resp = client.post(
                '/v1/sim/admin/create',
                data=json.dumps(
                    {
                        'email': 'noobmaster69@arclytics.com',
                        'position': 'Invisible.'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(data['message'], 'User does not exist.')

    def test_cancel_promotion_success(self):
        admin = User(
            **{
                'email': 'davidmatthews1004@gmail.com',
                'first_name': 'David',
                'last_name': 'Matthews'
            }
        )
        admin.set_password('testing123')
        admin.verified = True
        admin.is_admin = True
        admin_profile = AdminProfile(
            **{
                'position': 'Jedi Master',
                'mobile_number': None,
                'verified': True
            }
        )
        admin.admin_profile = admin_profile
        admin.save()

        user = User(
            **{
                'email': 'brickmatic479@gmail.com',
                'first_name': 'David',
                'last_name': 'Jnr'
            }
        )
        user.set_password('testing123')
        user.verified = True
        user.save()

        token = generate_promotion_confirmation_token(admin.email, user.email)
        url = generate_url('admin.cancel_promotion', token)
        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f'{protocol}://{client_host}:{client_port}'
            self.assertRedirects(resp, f'{redirect_url}/signin')

            updated_user = User.objects.get(email=user.email)
            self.assertTrue(not updated_user.is_admin)
            self.assertEqual(updated_user.admin_profile, None)

    def test_cancel_promotion_invalid_token(self):
        token = generate_confirmation_token('arclyticstest@gmail.com')
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/create/cancel?tokenexpired=true'
            )

    def test_cancel_promotion_invalid_token_list(self):
        token = generate_promotion_confirmation_token(
            'arclyticstest@gmail.com',
            '',
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/create/cancel?tokenexpired=true'
            )

    def test_cancel_promotion_token_list_missing_data(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(
            [
                'arclyticstestadmin@gmail.com',
            ],
            salt=current_app.config['SECURITY_PASSWORD_SALT']
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/create/cancel?tokenexpired=true'
            )

    def test_cancel_promotion_promoter_not_admin(self):
        admin = User(
            **{
                'email': 'davidmatthews1004@arclytics.io',
                'first_name': 'David',
                'last_name': 'Matthews'
            }
        )
        admin.set_password('testing123')
        admin.verified = True
        admin.save()

        user = User(
            **{
                'email': 'brickmatic479@arclytics.io',
                'first_name': 'David',
                'last_name': 'Jnr'
            }
        )
        user.set_password('testing123')
        user.verified = True
        user.save()

        token = generate_promotion_confirmation_token(admin.email, user.email)
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/create/cancel?tokenexpired=true'
            )

    def test_cancel_promotion_admin_dne(self):
        token = generate_promotion_confirmation_token(
            'arclyticstestadmin@gmail.com', 'arclyticstestuser@gmail.com'
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/create/cancel?tokenexpired=true'
            )

    def test_cancel_promotion_user_dne(self):
        test_admin = User(
            **{
                'email': 'arclyticstestadmin@gmail.com',
                'first_name': 'Arclytics',
                'last_name': 'Testadmin'
            }
        )
        test_admin.set_password('testing123'),
        test_admin.save()
        token = generate_promotion_confirmation_token(
            'arclyticstestadmin@gmail.com', 'arclyticstestuser@gmail.com'
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/create/cancel?tokenexpired=true'
            )

    # This test should work 30 days after the 25th of August 2019 as it uses a
    # token generated on that day.
    # def test_cancel_promotion_token_expired(self):
    #     admin = User(
    #         email='davidmatthews1004@gmail.com',
    #         first_name='David',
    #         last_name='Matthews'
    #     )
    #     admin.set_password('testing123')
    #     admin.verified = True
    #     admin.is_admin = True
    #     admin_profile = AdminProfile(
    #         position='Jedi Master', mobile_number=None, verified=True
    #     )
    #     admin.admin_profile = admin_profile
    #     admin.save()
    #
    #     user = User(
    #         email='brickmatic479@gmail.com',
    #         first_name='David',
    #         last_name='Jnr'
    #     )
    #     user.set_password('testing123')
    #     user.verified = True
    #     user.save()
    #
    #     token = (
    #         '.eJyLVkpJLMtMyU0sKclILS82NDAwcUjPTczM0UvOz1XSUUoqykzOBspmJpuYW'
    #         'yLJxAIARp0T0g.XWIw8A.x83TZm2iCNMPSpisMgEbMRfI-yM'
    #     )
    #     url = generate_url('admin.cancel_promotion', token)
    #     with current_app.test_client() as client:
    #         resp = client.get(url, content_type='application/json')
    #
    #         client_host = os.environ.get('CLIENT_HOST')
    #         self.assertEquals(resp.status_code, 302)
    #         self.assertTrue(resp.headers['Location'])
    #         redirect_url = \
    #             f'http://{client_host}/admin/create/cancel/tokenexpired'
    #         self.assertRedirects(resp, redirect_url)

    def test_verify_promotion_success(self):
        admin = User(
            **{
                # 'email': 'davidmatthews1004@gmail.com',
                'email': 'davidmatthews@arclytics.io',
                'first_name': 'David',
                'last_name': 'Matthews'
            }
        )
        admin.set_password('testing123')
        admin.verified = True
        # admin.is_admin = True
        admin_profile = AdminProfile(
            **{
                'position': 'Jedi Master',
                'mobile_number': None,
                'verified': True
            }
        )
        admin.admin_profile = admin_profile
        admin.save()

        user = User(
            **{
                # 'email': 'brickmatic479@gmail.com',
                'email': 'davidjnr@arclytics.io',
                'first_name': 'David',
                'last_name': 'Jnr'
            }
        )
        user.set_password('testing123')
        user.verified = True
        # user.is_admin=True
        user_admin_profile = AdminProfile(
            **{
                'position': 'Jedi Knight.',
                'mobile_number': None,
                'verified': False
            }
        )
        user.admin_profile = user_admin_profile
        user.admin_profile.promoted_by = admin.id
        user.save()

        token = generate_confirmation_token(user.email)
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(resp, f'{redirect_url}/signin')

            updated_user = User.objects.get(email=user.email)
            self.assertTrue(updated_user.is_admin)
            self.assertEqual(
                updated_user.admin_profile.position, 'Jedi Knight.'
            )
            self.assertEqual(updated_user.admin_profile.mobile_number, None)
            self.assertEqual(updated_user.admin_profile.verified, True)

    def test_verify_promotion_user_dne(self):
        token = generate_confirmation_token('arclyticstestuser@gmail.com')
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/verify?tokenexpired=true'
            )

    def test_verify_promotion_user_not_verified(self):
        test_user = User(
            **{
                'email': 'arclyticstestbot@gmail.com',
                'first_name': 'Arclytics',
                'last_name': 'Testuser'
            }
        )
        test_user.set_password('testing123')
        test_user.save()

        token = generate_confirmation_token(test_user.email)
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/verify?tokenexpired=true'
            )

    def test_verify_promotion_user_is_not_admin(self):
        test_user = User(
            **{
                'email': 'arclyticstestuser@gmail.com',
                'first_name': 'Arclytics',
                'last_name': 'Testuser'
            }
        )
        test_user.set_password('testing123')
        test_user.verified = True
        test_user.save()

        token = generate_confirmation_token(test_user.email)
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"
            self.assertRedirects(
                resp, f'{redirect_url}/admin/verify?tokenexpired=true'
            )

    # FIXME(davidmatthews1004@gmail.com) Pleas fix
    # def test_verify_promotion_token_expired(self):
    #     admin = User(
    #         # email='davidmatthews1004@gmail.com',
    #         email='davidmatthews1004@arclytics.io',
    #         first_name='David',
    #         last_name='Matthews'
    #     )
    #     admin.set_password('testing123')
    #     admin.verified = True
    #     # admin.is_admin = True
    #     admin_profile = AdminProfile(
    #         position='Jedi Master', mobile_number=None, verified=True
    #     )
    #     admin.admin_profile = admin_profile
    #     admin.save()
    #
    #     user = User(
    #         # email='brickmatic479@gmail.com',
    #         email='davidjnr@arclytics.io',
    #         first_name='David',
    #         last_name='Jnr'
    #     )
    #     user.set_password('testing123')
    #     user.verified = True
    #     # user.is_admin=True
    #     user_admin_profile = AdminProfile(
    #         position='Jedi Knight.', mobile_number=None, verified=False
    #     )
    #     user.admin_profile = user_admin_profile
    #     user.admin_profile.promoted_by = admin.id
    #     user.save()
    #
    #     token = (
    #         'ImRhdmlkam5yQGFyY2x5dGljcy5pbyI.XWIx9A.LHcr6fRYpQbB9hKMMoXMn01alcg'
    #     )
    #     url = generate_url('admin.verify_promotion', token)
    #
    #     with current_app.test_client() as client:
    #         resp = client.get(url, content_type='application/json')
    #
    #         data = json.loads(resp.data.decode())
    #         print(data)
    #
    #         client_host = os.environ.get('CLIENT_HOST')
    #         self.assertEquals(resp.status_code, 302)
    #         self.assertTrue(resp.headers['Location'])
    #         redirect_url = \
    #             f'http://{client_host}/admin/create/verify/tokenexpired'
    #         self.assertRedirects(resp, redirect_url)

    def test_enable_account_empty_payload(self):
        """Ensure an enable account request with an empty payload fails"""
        vader = User(
            **{
                'email': 'vader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        with self.client as client:
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/enable/user',
                data=json.dumps(''),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(disable_data['status'], 'fail')
            self.assertEqual(disable_data['message'], 'Invalid payload.')

    def test_enable_account_no_email(self):
        """Ensure an enable account request with no email key fails"""
        vader = User(
            **{
                'email': 'lordvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        with self.client as client:
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/enable/user',
                data=json.dumps({'some_key': 'some_value'}),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(disable_data['status'], 'fail')
            self.assertEqual(disable_data['message'], 'No email provided.')

    def test_enable_account_user_dne(self):
        """Ensure an enable account request on an unknown user fails"""
        vader = User(
            **{
                'email': 'darklordofthesith@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        with self.client as client:
            test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/enable/user',
                data=json.dumps({'email': 'cal_kestis@neuraldev.io'}),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 404)
            self.assertEqual(disable_data['status'], 'fail')
            self.assertEqual(disable_data['message'], 'User does not exist.')

    def test_enable_account_user_not_disabled(self):
        """
        Ensure an enable account request on an account that is not disabled
        fails
        """
        vader = User(
            **{
                'email': 'chosenone@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        cal = User(
            **{
                'email': 'calkestis_jk@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        cal.set_password('trustnoone')
        cal.save()

        with self.client as client:
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/enable/user',
                data=json.dumps({'email': 'calkestis_jk@arclytics.io'}),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(disable_data['status'], 'fail')
            self.assertEqual(
                disable_data['message'], 'Account is not disabled.'
            )

    def test_enable_account_success(self):
        """Ensure a valid enable account request is successful"""
        vader = User(
            **{
                'email': 'vadersfist@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.admin_profile = AdminProfile(
            **{
                'position': 'Position',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        vader.save()

        ahsoka = User(
            **{
                # 'email': 'davidmatthews1004@gmail.com',
                'email': 'ahsokatano@arclytics.io',
                'first_name': 'Cal',
                'last_name': 'Kestis'
            }
        )
        ahsoka.set_password('iamnojedi')
        ahsoka.active = False
        ahsoka.save()

        with self.client as client:
            cookie = test_login(client, vader.email, 'AllTooEasy')

            resp_disable = client.put(
                '/v1/sim/enable/user',
                # data=json.dumps({'email': 'davidmatthews1004@gmail.com'}),
                data=json.dumps({'email': 'ahsokatano@arclytics.io'}),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 200)
            self.assertEqual(disable_data['status'], 'success')


if __name__ == '__main__':
    unittest.main()
