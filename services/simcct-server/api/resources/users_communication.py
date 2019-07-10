# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# users_communication.py
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
"""users_communication.py: 

This resource module defines and implements resources for cross-container 
communication between simcct-server and the users-server.
"""

import os

import requests
from flask import Blueprint
from flask_restful import Resource

users_blueprint = Blueprint('users', __name__)


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

