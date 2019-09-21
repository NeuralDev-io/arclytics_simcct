# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# extensions.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""extensions.py: 

This module just defines extensions for Flask that can be used across the
context of the app.
"""
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_fluentd_logger import FlaskFluentdLogger

# from flask_talisman import Talisman
from .Session import FlaskRedisSession
from .mongo import MongoAlloys
from .mongodb import MongoSingleton
from .utilities import (DuplicateElementError, ElementInvalid,
                        ElementSymbolInvalid, JSONEncoder, MissingElementError,
                        PasswordValidationError, PeriodicTable,
                        RESPONSE_HEADERS, SimpleUTC, URLTokenError,
                        URLTokenExpired, get_mongo_uri)

# Some other extensions to Flask
api = Api()
bcrypt = Bcrypt()
redis_session = FlaskRedisSession()
fluentd_logging = FlaskFluentdLogger()
logger = fluentd_logging.get_logger()
# To use add flask-talisman==0.7.0 to requirements.txt
# talisman = Talisman()
