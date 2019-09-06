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
from flask import request, jsonify, session
from mongoengine import DoesNotExist

from sim_api.extensions.Session.redis_session import SESSION_COOKIE_NAME
from sim_api.models import User
from sim_api.extensions import RESPONSE_HEADERS
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)


def async_func(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# ========================== # FLASK VERSIONS # ============================= #
def authenticate_user_and_cookie_flask(f):
    """A wrapper decorator as a middleware to authenticate if the user has a
    cookie in their request. This will check the cookie and session is available
    for the user before it allows any actions on the back-end.

    Args:
        f: the endpoint View method to run that is being wrapped.

    Returns:
        the `sim_api.models.User` object if found.
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Session token is not valid.'
        }
        # Get the session key from the cookies
        session_key = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_key:
            return jsonify(response), 401

        if not session:
            response['message'] = 'Session is invalid.'
            return jsonify(response), 401

        # Extract the JWT from the session which we stored at login
        auth_token = session.get('jwt', None)
        if auth_token is None:
            response['message'] = 'No JWT stored in Session.'
            return jsonify(response), 500

        # Decode either returns bson.ObjectId if successful or a string from an
        # exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return jsonify(response), 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return jsonify(response), 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return jsonify(response), 403

        return f(user, *args, **kwargs)

    return decorated_func


def authorize_admin_cookie_flask(f):
    """A wrapper decorator as a middleware to authenticate if the user has a
    cookie in their request. This will check the cookie and session is
    available for the user before it allows any actions on the back-end.
    Additionally, it also checks if the user is an admin and allows to perform
    actions on admin authorized endpoints.

    Args:
        f: the endpoint View method to run that is being wrapped.

    Returns:
        the `sim_api.models.User` object if found.
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Session token is not valid.'
        }
        # Get the session key from the cookies
        session_key = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_key:
            return jsonify(response), 401

        if not session:
            response['message'] = 'Session is invalid.'
            return jsonify(response), 401

        # Extract the JWT from the session which we stored at login
        auth_token = session.get('jwt', None)
        if auth_token is None:
            response['message'] = 'No JWT stored in Session.'
            return jsonify(response), 500

        # Decode either returns bson.ObjectId if successful or a string
        # from an exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return jsonify(response), 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return jsonify(response), 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return jsonify(response), 403

        if not user.is_admin:
            response['message'] = 'Not authorized.'
            return jsonify(response), 403

        return f(user, *args, **kwargs)

    return decorated_func


# ======================== # RESTFUL VERSIONS # ============================= #
def authenticate_user_cookie_restful(f):
    """A wrapper decorator as a middleware to authenticate if the user has a
    cookie in their request. This will check the cookie and session is available
    for the user before it allows any actions on the back-end.

    Args:
        f: the endpoint View method to run that is being wrapped.

    Returns:
        the `sim_api.models.User` object if found.
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Session token is not valid.'
        }
        # Get the session key from the cookies
        session_key = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_key:
            return response, 401, RESPONSE_HEADERS

        if not session:
            response['message'] = 'Session is invalid.'
            return response, 401, RESPONSE_HEADERS

        # Extract the JWT from the session which we stored at login
        auth_token = session.get('jwt', None)
        if auth_token is None:
            response['message'] = 'No JWT stored in Session.'
            return response, 500, RESPONSE_HEADERS

        # Decode either returns bson.ObjectId if successful or a string from an
        # exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return response, 401, RESPONSE_HEADERS

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return response, 404, RESPONSE_HEADERS

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return response, 403, RESPONSE_HEADERS

        return f(user, *args, **kwargs)

    return decorated_func


def authorize_admin_cookie_restful(f):
    """A wrapper decorator as a middleware to authenticate if the user has a
    cookie in their request. This will check the cookie and session is
    available for the user before it allows any actions on the back-end.
    Additionally, it also checks if the user is an admin and allows to perform
    actions on admin authorized endpoints.

    Args:
        f: the endpoint View method to run that is being wrapped.

    Returns:
        the `sim_api.models.User` object if found.
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {
            'status': 'fail',
            'message': 'Session token is not valid.'
        }
        # Get the session key from the cookies
        session_key = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_key:
            return response, 401

        if not session:
            response['message'] = 'Session is invalid.'
            return response, 401

        # Extract the JWT from the session which we stored at login
        auth_token = session.get('jwt', None)
        if auth_token is None:
            response['message'] = 'No JWT stored in Session.'
            return response, 500

        # Decode either returns bson.ObjectId if successful or a string
        # from an exception
        resp = User.decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return response, 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return response, 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return response, 403

        if not user.is_admin:
            response['message'] = 'Not authorized.'
            return response, 403

        return f(user, *args, **kwargs)

    return decorated_func

# =========================================================================== #
# ========================= # OLD MIDDLEWARE # ============================== #
# =========================================================================== #


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
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return response, 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return response, 403

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
        try:
            user: User = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return jsonify(response), 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            return jsonify(response), 403

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

        try:
            admin = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['message'] = 'User does not exist.'
            return response, 404

        if not admin.is_admin:
            response['message'] = 'Not authorized.'
            return response, 403

        return f(resp, *args, **kwargs)

    return decorated_func


def token_required_flask(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # Get the auth header
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            response['message'] = 'No valid Authorization in header.'
            return jsonify(response), 401

        token = auth_header.split(' ')[1]

        if token == '':
            response['message'] = 'Invalid JWT token in header.'
            return jsonify(response), 401

        # TODO(andrew@neuraldev.io -- Sprint 6): Find a way to validate this is
        #  is a valid token for a user.
        #  - We can check the session store to confirm if the token is valid
        #    for a user.

        return f(token, *args, **kwargs)

    return decorated_func


def session_key_required_flask(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_key = request.headers.get('Session', None)

        if not session_key:
            response['message'] = 'No Session in header.'
            return jsonify(response), 401

        return f(session_key, *args, **kwargs)

    return decorated_func


def session_and_token_required_flask(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # Get the auth header
        auth_header = request.headers.get('Authorization', None)
        session_key = request.headers.get('Session', None)

        if not auth_header:
            response['message'] = 'No valid Authorization in header.'
            return jsonify(response), 401

        token = auth_header.split(' ')[1]

        if token == '':
            response['message'] = 'Invalid JWT token in header.'
            return jsonify(response), 401

        if not session_key:
            response['message'] = 'No Session key in header.'
            return response, 401

        return f(token, session_key, *args, **kwargs)

    return decorated_func


def token_and_session_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # Get the auth header
        auth_header = request.headers.get('Authorization', None)
        session_key = request.headers.get('Session', None)

        if not auth_header:
            response['message'] = 'No Authorization in header.'
            return response, 401

        token = auth_header.split(' ')[1]

        if token == '':
            response['message'] = 'Invalid JWT token in header.'
            return response, 401

        # TODO(andrew@neuraldev.io -- Sprint 6): Find a way to validate this is
        #  is a valid token for a user.

        if not session_key:
            response['message'] = 'No Session key in header.'
            return response, 401

        return f(token, session_key, *args, **kwargs)

    return decorated_func


def token_required_restful(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # Get the auth header
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            response['message'] = 'No valid Authorization in header.'
            return response, 401

        token = auth_header.split(' ')[1]

        if token == '':
            response['message'] = 'Invalid JWT token in header.'
            return response, 401

        # TODO(andrew@neuraldev.io -- Sprint 6): Find a way to validate this is
        #  is a valid token for a user.

        return f(token, *args, **kwargs)

    return decorated_func
