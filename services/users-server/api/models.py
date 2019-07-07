# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# models.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""models.py: 

This module stores the mongoengine.Document models for the Arclytics API microservice.
"""

import datetime
import jwt
from typing import Union

import json
from bson import ObjectId
from mongoengine import (Document,
                         EmbeddedDocument,
                         StringField,
                         EmailField,
                         BooleanField,
                         DateTimeField,
                         EmbeddedDocumentField,
                         EmbeddedDocumentListField)
from flask import current_app

from logger.arc_logger import AppLogger
from api import bcrypt, JSONEncoder

logger = AppLogger(__name__)
# User type choices
USERS = (('1', 'ADMIN'), ('2', 'USER'))


# ========== # CUSTOM EXCEPTIONS # ========== #
class PasswordValidationError(Exception):
    """Raises an Exception if now password was set before trying to save the User model."""

    def __init__(self):
        super(PasswordValidationError,
              self).__init__('A password must be set before saving.')


# ========== # DOCUMENTS MODELS SCHEMA # ========== #
class User(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(default=None,
                           max_length=64,
                           null=False,
                           min_length=6)
    # first_name = StringField(required=True, max_length=255)
    # last_name = StringField(required=True, max_length=255)
    username = StringField(required=True, unique=True, min_length=1, max_length=180)
    user_type = StringField(required=True, max_length=1, choices=USERS, default=USERS[1][0])
    # profile = EmbeddedDocumentListField()
    # TODO: Make these
    # saved_configurations = EmbeddedDocumentListField(document_type=Configurations)
    # saved_compositions = EmbeddedDocumentListField(document_type=Compositions)

    # Some rather useful metadata information that's not core to the definition of a user
    active = BooleanField(default=True)
    is_admin = BooleanField(default=False, name='admin')
    verified = BooleanField(default=False)
    created = DateTimeField(default=datetime.datetime.utcnow())
    last_updated = DateTimeField(default=None)
    last_login = DateTimeField(default=None)
    # Define the collection and indexing for this document
    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'last_login',
        ]
    }

    def set_password(self, raw_password: str) -> None:
        """Helper utility method to save an encrypted password using the Bcrypt Flask extension."""
        self.password = bcrypt.generate_password_hash(
            password=raw_password,
            rounds=current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

    def to_dict(self, *args, **kwargs) -> dict:
        """Simple Document.User helper method to get a Python dict back."""
        return {
            '_id': self.id,
            'email': self.email,
            'username': self.username,
            'admin': self.is_admin,
            'created': self.created,
            'active': self.active,
            'last_updated': self.last_updated,
            'last_login': self.last_login,
        }

    def to_response(self, *args, **kwargs) -> json:
        """Simple helper method to get a json class from a string returned by mongoengine.Document.to_json()."""
        return json.loads(self.to_json())

    @staticmethod
    def encode_auth_token(user_id: ObjectId) -> Union[bytes, None]:
        """Generates JWT auth token that is returned as bytes."""
        try:
            payload = {
                'exp':
                datetime.datetime.utcnow() + datetime.timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS', 0),
                    seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS',
                                                   0)),
                'iat':
                datetime.datetime.utcnow(),
                'sub':
                user_id
            }

            return jwt.encode(payload=payload,
                              key=current_app.config.get('SECRET_KEY', None),
                              algorithm='HS256',
                              json_encoder=JSONEncoder)
        except Exception as e:
            logger.error('Encode auth token error: {}'.format(e))
            return None

    @staticmethod
    def decode_auth_token(auth_token: bytes) -> Union[ObjectId, str]:
        """Decodes the JWT auth token.

        Args:
            auth_token: a bytes type that was encoded by

        Returns:
            An integer or string.
        """
        try:
            payload = jwt.decode(jwt=auth_token,
                                 key=current_app.config.get('SECRET_KEY', None))
            return ObjectId(payload['sub'])
        except jwt.ExpiredSignatureError as e:
            # logger.error('Signature expired error.')
            return 'Signature expired. Please login again.'
        except jwt.InvalidTokenError as e:
            # logger.error('Invalid token error.')
            return 'Invalid token. Please log in again.'

    # MongoEngine allows you to create custom cleaning rules for your documents when calling save().
    # By providing a custom clean() method you can do any pre validation / data cleaning.
    # This might be useful if you want to ensure a default value based on other document values.
    def clean(self):
        """Ensures a `password` has been stored before saving."""
        if self.password is None:
            raise PasswordValidationError()

        if self.last_updated is None:
            self.last_updated = self.created

    # def __str__(self):
    #     pass

# ========== # EMBEDDED DOCUMENTS MODELS SCHEMA # ========== #
