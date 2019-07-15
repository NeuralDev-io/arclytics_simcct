# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_base.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.12'
"""test_api_base.py: 

This module is the base TestCase so that we can inherit from it and the settings
for testing that are initialised in create_app() -- interface by Flask-Testing.
"""

import os

import redis
from flask_testing import TestCase

from sim_app.app import create_app, mongo, sess

app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')

        self.redis = redis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=int(os.environ.get('REDIS_PORT')),
            db=app.config['REDIS_DB']
        )
        app.config['SESSION_REDIS'] = self.redis
        sess.init_app(app)
        mongo.init_app(app)
        self.assertEqual(mongo.db.name, 'arc_test')
        return app

    def tearDown(self) -> None:
        self.redis.flushall()
        self.redis.flushdb()
