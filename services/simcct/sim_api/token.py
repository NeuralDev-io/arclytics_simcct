# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# token.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
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

from sim_api.extensions.utilities import URLTokenError, URLTokenExpired


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
        raise URLTokenExpired('Signature expired.')
    except BadSignature as e:
        raise URLTokenError('Bad signature.')
    except Exception as e:
        raise URLTokenError(str(e))
    return email


def generate_url(endpoint, token):
    if os.environ.get('FLASK_EVN', 'development') == 'production':
        return url_for(endpoint, token=token, _external=True, _scheme='https')
    return url_for(endpoint, token=token, _external=True)


def generate_url_with_signature(endpoint, signature):
    if os.environ.get('FLASK_EVN', 'development') == 'production':
        return url_for(
            endpoint, signature=signature, _external=True, _scheme='https'
        )
    return url_for(endpoint, signature=signature, _external=True)


def generate_promotion_confirmation_token(admin_email: str, user_email: str
                                          ) -> Union[bool, list]:
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(
        [admin_email, user_email], salt=app.config['SECURITY_PASSWORD_SALT']
    )


def generate_shared_simulation_token(sim_id: str) -> Union[bool, list]:
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(sim_id, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_simulation_token(token) -> Union[bool, dict]:
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        sim_data = serializer.loads(
            token, salt=app.config['SECURITY_PASSWORD_SALT']
        )
    except BadSignature as e:
        raise URLTokenError('Bad signature.')
    except Exception as e:
        raise URLTokenError('Token error.')
    return sim_data
