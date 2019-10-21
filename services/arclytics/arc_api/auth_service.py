# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# auth_service.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.10.02'

"""auth_service.py: 

This module provides an authentication and authorisation service that can 
take in a JWT token and decode it.
"""

from typing import Union, Tuple
from datetime import datetime, timedelta

import jwt
from bson import ObjectId
from flask import current_app as app

from arc_api.extensions import apm, JSONEncoder
from arc_logging import AppLogger

logger = AppLogger(__name__)


class AuthService(object):
    @staticmethod
    def encode_auth_token(
            user_id: ObjectId, role: str = 'user'
    ) -> Union[bytes, None]:
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
    def decode_auth_token(
            auth_token: Union[bytes, str]
    ) -> Union[Tuple[ObjectId, str], Tuple[str, None]]:
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
            return ObjectId(payload['sub']), payload['role']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please login again.', None
        except jwt.InvalidTokenError:
            logger.info('Invalid token error.')
            apm.capture_exception()
            return 'Invalid token. Please log in again.', None
