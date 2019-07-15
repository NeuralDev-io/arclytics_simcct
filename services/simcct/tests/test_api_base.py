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

from flask_testing import TestCase

from sim_app.app import create_app, mongo, sess

app = create_app()


class BaseTestCase(TestCase):
    redis = None

    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')
        sess.init_app(app)
        mongo.init_app(app)
        self.assertEqual(mongo.db.name, 'arc_test')
        return app

    @classmethod
    def tearDownClass(cls) -> None:
        redis = app.config['SESSION_REDIS']
        redis.flushall()
        redis.flushdb()
        mongo.cx.drop_database('arc_test')

    # def tearDown(self) -> None:
    #     self.redis.flushall()
    #     self.redis.flushdb()
    #     mongo.drop_databases('arc_test')
