# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# auth_service.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.10.02'
"""auth_service.py: 

This module provides an authentication and authorisation service that can 
take in a JWT token and decode it.
"""

from typing import Union
from datetime import datetime, timedelta

import jwt
from bson import ObjectId
from flask import current_app as app

from sim_api.extensions import apm, JSONEncoder
from arc_logging import AppLogger

logger = AppLogger(__name__)


class AuthService(object):
    @staticmethod
    def encode_auth_token(user_id: ObjectId,
                          role: str = 'user') -> Union[bytes, None]:
        """Generates JWT auth token that is returned as bytes.

        Args:
            user_id: an ObjectId for the User.
            role: the role of user. Must be one of: `admin` or `user`.

        Returns:
            A valid JWT token as bytes.
        """
        try:
            payload = {
                'exp':
                datetime.utcnow() + timedelta(
                    days=app.config.get('TOKEN_EXPIRATION_DAYS', 0),
                    seconds=app.config.get('TOKEN_EXPIRATION_SECONDS', 0)
                ),
                'iat':
                datetime.utcnow(),
                'sub':
                user_id,
                'role':
                role
            }

            return jwt.encode(
                payload=payload,
                key=app.config.get('SECRET_KEY', None),
                algorithm='HS256',
                json_encoder=JSONEncoder
            )
        except Exception as e:
            logger.exception('Encode auth token error: {}'.format(e))
            apm.capture_exception()
            return None

    @staticmethod
    def decode_auth_token(auth_token: Union[bytes, str]
                          ) -> Union[ObjectId, str]:
        """Decodes the JWT auth token.

        Args:
            auth_token: a bytes type that was encoded by

        Returns:
            An integer or string.
        """
        try:
            payload = jwt.decode(
                jwt=auth_token, key=app.config.get('SECRET_KEY', None)
            )
            return ObjectId(payload['sub'])
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please login again.'
        except jwt.InvalidTokenError:
            logger.info('Invalid token error.')
            apm.capture_exception()
            return 'Invalid token. Please log in again.'

    @staticmethod
    def encode_password_reset_token(user_id: ObjectId) -> Union[bytes, None]:
        """Encode a timed JWT token of 30 minutes to send to the client-side
        so we can verify which user has requested to reset their password.

        Args:
            user_id: the valid ObjectId user id.

        Returns:
            A valid JWT token or None if there is any kind of generic exception.
        """
        # noinspection PyBroadException
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=30),
                'iat': datetime.utcnow(),
                'sub': user_id
            }

            return jwt.encode(
                payload=payload,
                key=app.config.get('SECRET_KEY', None),
                algorithm='HS256',
                json_encoder=JSONEncoder
            )
        except Exception:
            logger.exception(
                'Encode authentication token error.', exc_info=True
            )
            apm.capture_exception()
            return None

    @staticmethod
    def decode_password_reset_token(auth_token: bytes) -> Union[ObjectId, str]:
        """Decodes the JWT auth token for the password reset.

        Args:
            auth_token: a bytes type that was encoded by

        Returns:
            An ObjectId or string.
        """
        try:
            payload = jwt.decode(
                jwt=auth_token, key=app.config.get('SECRET_KEY', None)
            )
            return ObjectId(payload['sub'])
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please get a new token.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please get a new token.'
