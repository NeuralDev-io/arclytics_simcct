# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# session.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.10'
"""session.py: 

This module defines the resources for session management. 
"""

import os

import requests
from flask import Blueprint, session, request
from flask_restful import Resource
from bson import ObjectId

session_blueprint = Blueprint('session', __name__)


class Session(Resource):

    def post(self):
        post_data = request.get_json()

        response = {
                'status': 'fail',
                'message': 'Invalid payload.'
        }

        if not post_data:
            return response, 400

        user_id = post_data.get('_id', None)
        token = post_data.get('token', None)

        if not user_id:
            response['message'] = 'User ObjectId must be provided.'
            return response, 401

        if not token:
            response['message'] = 'JWT token must be provided.'
            return response, 401

        session['user_id'] = user_id
        session['token'] = token

        response['status'] = 'success'
        response['message'] = 'User session initiated.'
        response['session_id'] = session.sid

        return response, 201

    def get(self):
        # TODO(andrew@neuraldev.io): Not really sure if I want this endpoint.
        response = {
            'status': 'success',
            'session_id': session.sid
        }

        return response, 200


class UsersPing(Resource):
    """
    This is just a sanity check to ensure we can connect from this server to
    the users-server through Docker just fine.
    """

    def get(self):
        users_server = os.environ.get('USERS_HOST', None)
        # We use the built-in DNS server of Docker to resolve the correct
        # IP address of the other container [1].
        url = f'http://{users_server}/ping'
        res = requests.get(url)
        return res.json(), 200, {'content-type': 'application/json'}
