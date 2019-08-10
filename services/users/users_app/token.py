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

from typing import Union

from flask import url_for
from flask import current_app as app
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired


class URLTokenError(Exception):
    """
    A custom exception to be raised from any itsdangerous package exceptions.
    """

    def __init__(self, msg: str = None):
        super(URLTokenError, self).__init__(msg)


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
    except BadSignature as e:
        raise URLTokenError('Bad signature.')
    except SignatureExpired as e:
        raise URLTokenError('Signature expired.')
    except Exception as e:
        raise URLTokenError('Token error.')
    return email


def generate_url(endpoint, token):
    return url_for(endpoint, token=token, _external=True)


def generate_promotion_confirmation_token(admin_email: str, user_email: str
                                          ) -> Union[bool, list]:
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(
        [admin_email, user_email], salt=app.config['SECURITY_PASSWORD_SALT']
    )
