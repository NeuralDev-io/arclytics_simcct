# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# app.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'

"""app.py: 

This is the entrypoint to our Python Flask API server.
"""
__name__ = 'Arclytics_API'

import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


class JSONEncoder(json.JSONEncoder):
    """Extend json-encoder class to properly convert dates and object ids."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# instantiate the application
app = Flask(__name__)

# API interface
api = Api(app=app)

# setup the configuration
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# Mongo interface
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)
user_db = mongo.db.users

# setup some config variables for flask_jwt_extended
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

# Setup a Bcrypt object to encrypt passwords
flask_bcrypt = Bcrypt(app)

# Setup the JWT manager
jwt = JWTManager(app)

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder

from api.views import *
