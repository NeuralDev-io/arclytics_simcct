# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_base.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.12'
"""test_api_base.py: 

{Description}
"""

import os

import redis
from flask_session import Session
from flask_testing import TestCase

from sim_api import create_app

app = create_app()
sess = Session()


class BaseTestCase(TestCase):
    redis = None
    host = os.environ.get('REDIS_HOST')
    port = int(os.environ.get('REDIS_PORT'))
    db = int(app.config['REDIS_DB'])

    def create_app(self):
        app.config.from_object('configs.flask_configs.TestingConfig')
        self.redis = redis.Redis(host=self.host, port=self.port, db=self.db)
        self.redis.client_setname('arc_sim_redis_testing')
        return app

    def tearDown(self) -> None:
        self.redis.flushall()
        self.redis.flushdb()
