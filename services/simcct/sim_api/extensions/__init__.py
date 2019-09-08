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
from .utilities import (
    get_mongo_uri, JSONEncoder, PasswordValidationError, URLTokenError,
    URLTokenExpired, ElementSymbolInvalid, ElementInvalid, MissingElementError,
    DuplicateElementError, SimpleUTC, PeriodicTable, RESPONSE_HEADERS
)

from .mongo import MongoAlloys
from .mongodb import MongoSingleton
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_mail import Mail
from .Session import FlaskRedisSession

# Some other extensions to Flask
bcrypt = Bcrypt()
api = Api()
mail = Mail()
redis_session = FlaskRedisSession()
