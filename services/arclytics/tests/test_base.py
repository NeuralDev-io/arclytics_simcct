# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# base.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__status__ = 'development'
__date__ = '2019.07.03'

from datetime import datetime
from os import environ as env

import requests
from bson import ObjectId
from flask_testing import TestCase
from pymongo import MongoClient

from arc_api import create_app
from arc_logging import AppLogger
from tests.test_arc_utilities import (GMT_DATETIME_FORMAT, URL_PREFIX,
                                      get_mongo_uri)
from arc_api.extensions import API_TOKEN_NAME

logger = AppLogger(__name__)

app = create_app(configs_path='configs.flask_conf.TestingConfig')


class BaseTestCase(TestCase):
    client = app.test_client(use_cookies=True)
    mongo_client = None
    strange_email = 'strange@arclytics.io'
    strange_password = 'WereInTheEndGameNow'

    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')
        return app

    @classmethod
    def setUpClass(cls) -> None:
        cls.mongo_client = MongoClient(get_mongo_uri())

        requests.post(
            f'{URL_PREFIX}/auth/register',
            json={
                'first_name': 'Stephen',
                'last_name': 'Strange',
                'email': 'strange@arclytics.io',
                'password': cls.strange_password
            },
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )

        # After creating a user, we need to make them an admin otherwise
        # we cannot get any JWT token for normal users.
        db_name = (
            'arc_dev'
            if env.get('FLASK_ENV', 'development') == 'development'
            else env.get('MONGO_APP_DB', 'arclytics')
        )
        db = cls.mongo_client[db_name]
        user = db.users.find_one({'email': cls.strange_email})
        # print(user)
        user.update({
            'admin_profile': {
                'position': 'Stone Keeper',
                'mobile_number': '1234567890',
                'verified': True
            },
            'admin': True,
            'verified': True
        })
        _id = user.pop('_id')
        db.users.replace_one({'_id': ObjectId(_id)}, user, upsert=True)

        # Now we need to login to get the Token we need
        session = requests.Session()
        res = session.post(
            f'{URL_PREFIX}/auth/login',
            json={
                'email': cls.strange_email,
                'password': cls.strange_password
            },
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )

        # Extract the token from the header and set the cookie on the
        # client.
        resp_set_cookie = res.headers['Set-Cookie'].split(';')
        expiry_str = resp_set_cookie[1].split('=')[1]
        expiry_date = datetime.strptime(expiry_str, GMT_DATETIME_FORMAT)
        auth_token = resp_set_cookie[3].split('=')[2]
        cls.client.set_cookie(
            API_TOKEN_NAME, auth_token, expires=expiry_date, httponly=True
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up logic for the test suite declared in the test module."""
        # Executed after all tests in one test run.

        # With the simcct server running, in this environment it would be in
        # a development database
        db_name = (
            'arc_dev'
            if env.get('FLASK_ENV', 'development') == 'development'
            else env.get('MONGO_APP_DB', 'arclytics')
        )
        db = cls.mongo_client[db_name]
        user = db.users.find_one({'email': cls.strange_email})
        db.users.delete_one({'_id': ObjectId(user['_id'])})
