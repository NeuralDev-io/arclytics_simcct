# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# extensions.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.1.0'
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
from elasticapm.contrib.flask import ElasticAPM

# from flask_talisman import Talisman
from .Session import FlaskRedisSession
from .mongo import MongoAlloys
from .mongodb import MongoSingleton
from .utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid, JSONEncoder,
    MissingElementError, PasswordValidationError, PeriodicTable,
    RESPONSE_HEADERS, SimpleUTC, URLTokenError, URLTokenExpired, get_mongo_uri
)

# Some other extensions to Flask
apm = ElasticAPM()
api = Api()
bcrypt = Bcrypt()
redis_session = FlaskRedisSession()
# To use add flask-talisman==0.7.0 to requirements.txt
# talisman = Talisman()
