# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# views.py
# 
# Attributions: 
# [1] https://stackoverflow.com/questions/53568275/
# two-seperate-flask-apps-communicating-in-docker-containers
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.10'
"""views.py: 

{Description}
"""

import os

import requests
from flask import Blueprint, current_app
from flask_restful import Resource, Api

test_blueprint = Blueprint('users', __name__)
api = Api(test_blueprint)


class UsersPing(Resource):
    """Simple resource that pings the Users-Server to get a response."""

    def get(self):
        users_server = os.environ.get('USERS_HOST', None)
        # We use the built-in DNS server of Docker to resolve the correct
        # IP address of the other container [1].

        url = f'http://{users_server}/ping'
        res = requests.get(url)
        print(res)
        return res.json(), 200, {'content-type': 'application/json'}


api.add_resource(UsersPing, '/users/ping')
