# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# token.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.22'
"""token.py: 

This module defines some helper methods to generate email tokens to be used in 
features such as registration, sharing, and changing passwords.
"""

import os
from typing import Union

from flask import current_app as app
from flask import url_for
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired

from sim_api.extensions import apm
from sim_api.extensions.utilities import URLTokenError, URLTokenExpired

from arc_logging import AppLogger

logger = AppLogger(__name__)


def generate_confirmation_token(email: str):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token: bytes, expiration: int = 3600) -> Union[bool, str]:
    """Confirm the token by decoding it with an expiration timer of 3600 seconds
    or 1 hour.

    Args:
        token: the token to decode.
        expiration: the number of seconds the token is alive for.

    Returns:
        A valid email if it is a valid token otherwise a Boolean.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except SignatureExpired as e:
        message = 'Signature expired.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        raise URLTokenExpired(message)
    except BadSignature as e:
        message = 'Bad signature.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        raise URLTokenError(message)
    except Exception as e:
        message = 'An Exception Occurred.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        raise URLTokenError(str(e))
    return email


def generate_url(endpoint, token):
    """Generate a url for an endpoint with a token. E.g. a confirmation url
    for a user to verify their account.

    Args:
        endpoint: An endpoint referencing a method in the backend

        token: A token that has been serialized with relevant data (e.g. a
        user's email address) and the secret salt.

    Returns:
        url for the given endpoint with token attached.
    """
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        return url_for(endpoint, token=token, _external=True, _scheme='https')
    return url_for(endpoint, token=token, _external=True)


def generate_url_with_signature(endpoint, signature):
    """Generate a url for an endpoint with a signature.

    Args:
        endpoint: An endpoint referencing a method in the backend.

        signature: A signature serialized with releant data and the secret
        salt.

    Returns:
        url for the given endpoint with signature attached.
    """
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        return url_for(
            endpoint, signature=signature, _external=True, _scheme='https'
        )
    return url_for(endpoint, signature=signature, _external=True)


def generate_promotion_confirmation_token(admin_email: str, user_email: str
                                          ) -> Union[bool, list]:
    """Generate a token for a promotion confirmation.

    Args:
        admin_email: The email address of the admin performing the promotion

        user_email: The email address of  the user receiving the promotion

    Returns:
        A token serialized with the two email addresses and salt.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(
        [admin_email, user_email], salt=app.config['SECURITY_PASSWORD_SALT']
    )


def generate_shared_simulation_token(sim_id: str) -> Union[bool, list]:
    """Generate a token for a shared simulation.

    Args:
        sim_id: The object id for the simulation that is being shared.

    Returns:
        A token serialized with the sim_id and salt.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(sim_id, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_simulation_token(token) -> Union[bool, dict]:
    """Confirm a token for a shared simulation

    Args:
        The serialized token that should contain the object id for the
        simulation that is shared.

    Returns:
        The simulation id decoded from the token.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        sim_data = serializer.loads(
            token, salt=app.config['SECURITY_PASSWORD_SALT']
        )
    except BadSignature as e:
        message = 'Bad signature.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        raise URLTokenError(message)
    except Exception as e:
        message = 'Token error.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        raise URLTokenError('Token error.')
    return sim_data
