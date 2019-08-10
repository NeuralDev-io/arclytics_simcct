# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# auth_decorators.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.06'
"""auth_decorators.py: 

{Description}
"""

from functools import wraps
from threading import Thread

from bson import ObjectId
from flask import request, jsonify

from users_app.models import User


def authenticate(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Provide a valid JWT auth token.'
        }
        # get auth token
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            return response, 401

        # auth_header = 'Bearer token'
        auth_token = auth_header.split(' ')[1]

        # Decode either returns bson.ObjectId if successful or a string from an
        # exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return response, 401

        # Validate the user is active
        user = User.objects.get(id=resp)
        if not user:
            response['message'] = 'User does not exist.'
            return response, 404
        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return response, 401

        return f(resp, *args, **kwargs)

    return decorated_func


def authenticate_flask(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Provide a valid JWT auth token.'
        }
        # get auth token
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            return jsonify(response), 401

        # auth_header = 'Bearer token'
        auth_token = auth_header.split(' ')[1]

        # Decode either returns bson.ObjectId if successful or a string from an
        # exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return jsonify(response), 401

        # Validate the user is active
        user = User.objects.get(id=resp)
        if not user or not user.active:
            response['message'] = 'This user account has been disabled.'
            return jsonify(response), 401

        return f(resp, *args, **kwargs)

    return decorated_func


def authenticate_admin(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Provide a valid JWT auth token.'
        }

        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            return response, 401

        # auth_header = 'Bearer token'
        auth_token = auth_header.split(' ')[1]

        resp = User.decode_auth_token(auth_token=auth_token)

        if isinstance(resp, str):
            response['message'] = resp
            return response, 401

        admin = User.objects.get(id=resp)
        if not admin or not admin.is_admin:
            response['message'] = 'Not authorized.'
            return response, 403

        return f(resp, *args, **kwargs)

    return decorated_func


def logout_authenticate(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Provide a valid JWT auth token.'
        }
        # get auth token
        auth_header = request.headers.get('Authorization', None)
        session_key = request.headers.get('Session', None)

        if not auth_header:
            return jsonify(response), 400

        if not session_key:
            response['message'] = 'Provide a valid Session key.'
            return jsonify(response), 400

        # auth_header = 'Bearer token'
        auth_token = auth_header.split(' ')[1]

        # Decode either returns bson.ObjectId if successful or a string from an
        # exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return jsonify(response), 401

        # Validate the user is active
        user = User.objects.get(id=resp)
        if not user or not user.active:
            response['message'] = 'This user does not exist.'
            return jsonify(response), 401

        return f(resp, auth_token, session_key, *args, **kwargs)

    return decorated_func
