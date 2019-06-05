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
import bcrypt
from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo

from api.helpers import *

# instantiate the application
app = Flask(__name__)

# API interface
api = Api(app=app)
# Mongo interface
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

users = mongo.db.users

# setup the configuration
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)


class PingTest(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong'
        }


class UserRegister(Resource):
    pass
    # def post(self):
    #     # get data from request body
    #     data = request.get_json()
    #
    #     username = data['username']
    #     password = data['password']
    #
    #     # check if the user exists
    #     if user_exist(username):
    #         return jsonify({
    #             'status': 301,
    #             'msg': 'Invalid username'
    #         })



api.add_resource(PingTest, '/arc/ping')
