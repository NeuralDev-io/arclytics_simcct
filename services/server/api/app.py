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
from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from pprint import pprint

from api.helpers import *

# instantiate the application
app = Flask(__name__)

# API interface
api = Api(app=app)


# setup the configuration
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)
# pprint(app.config)

# Mongo interface
mongo = PyMongo(app)


@app.route('/')
def index():
    return jsonify({'message': 'Hello World!'})


class PingTest(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong'
        }


api.add_resource(PingTest, '/arc/ping')
