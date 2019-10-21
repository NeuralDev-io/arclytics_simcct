# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# middleware.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.06'
"""middleware.py: 

This is the request middleware that ensures every single request is checked 
for cookies and authentication or authorisation based on the endpoint View 
methods used.
"""

from functools import wraps
from threading import Thread

from bson import ObjectId
from flask import json, jsonify, request, session
from mongoengine import DoesNotExist

from arc_logging import AppLogger
from sim_api.extensions.Session.redis_session import SESSION_COOKIE_NAME
from sim_api.extensions import apm
from sim_api.models import User
from sim_api.auth_service import AuthService

logger = AppLogger(__name__)


def async_func(f):
    """Threading decorator if you want to make a method use separate thread."""
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
        response = {'status': 'fail', 'message': 'Session token is not valid.'}
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
        resp = AuthService().decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return jsonify(response), 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'User does not exist.'
            logger.exception(response['message'])
            apm.capture_exception()
            return jsonify(response), 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            logger.info(
                json.dumps(
                    {
                        "message": response['message'],
                        "user": user.email
                    }
                )
            )
            apm.capture_message('Unauthorised access.')
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
        response = {'status': 'fail', 'message': 'Session token is not valid.'}
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
        resp = AuthService().decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            logger.info(resp)
            apm.capture_message('Invalid Auth token.')
            return jsonify(response), 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'User does not exist.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return jsonify(response), 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            logger.info(
                json.dumps(
                    {
                        "message": response['message'],
                        "user": user.email
                    }
                )
            )
            apm.capture_message('Unauthorised access.')
            return jsonify(response), 403

        if not user.is_admin:
            response['message'] = 'Not authorized.'
            logger.info(
                json.dumps(
                    {
                        "message": response['message'],
                        "user": user.email
                    }
                )
            )
            # Must capture message because there is no exception in this
            # case which is a bug if Python APM Agent.
            # https://github.com/elastic/apm-agent-python/issues/599
            apm.capture_message('Unauthorised admin access.')
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
        response = {'status': 'fail', 'message': 'Session token is not valid.'}
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

        # Decode either returns bson.ObjectId if successful or a string from an
        # exception
        resp = AuthService().decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return response, 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'User does not exist.'
            logger.exception(response['message'])
            apm.capture_exception()
            return response, 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            logger.info(
                json.dumps(
                    {
                        "message": response['message'],
                        "user": user.email
                    }
                )
            )
            # Must capture message because there is no exception in this
            # case which is a bug if Python APM Agent.
            # https://github.com/elastic/apm-agent-python/issues/599
            apm.capture_message('Unauthorised access.')
            return response, 403

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
        response = {'status': 'fail', 'message': 'Session token is not valid.'}
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
        resp = AuthService().decode_auth_token(auth_token=auth_token)

        # Either returns an ObjectId User ID or a string response.
        if not isinstance(resp, ObjectId):
            response['message'] = resp
            return response, 401

        # Validate the user is active
        try:
            user = User.objects.get(id=resp)
        except DoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'User does not exist.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 404

        if not user.active:
            response['message'] = 'This user account has been disabled.'
            logger.info(
                json.dumps(
                    {
                        "message": response['message'],
                        "user": user.email
                    }
                )
            )
            # Must capture message because there is no exception in this
            # case which is a bug if Python APM Agent.
            # https://github.com/elastic/apm-agent-python/issues/599
            apm.capture_message('Unauthorised access.')
            return response, 403

        if not user.is_admin:
            response['message'] = 'Not authorized.'
            logger.info(
                json.dumps(
                    {
                        "message": response['message'],
                        "user": user.email
                    }
                )
            )
            # Must capture message because there is no exception in this
            # case which is a bug if Python APM Agent.
            # https://github.com/elastic/apm-agent-python/issues/599
            apm.capture_message('Unauthorised admin access.')
            return response, 403

        return f(user, *args, **kwargs)

    return decorated_func
