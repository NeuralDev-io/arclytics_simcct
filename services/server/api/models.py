# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# models.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
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

from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from flask import current_app

from logger.arc_logger import AppLogger
from api import bcrypt

logger = AppLogger(__name__)


# User type choices
USERS = (('1', 'ADMIN'), ('2', 'USER'))


# ========== # CUSTOM EXCEPTIONS # ========== #
class PasswordValidationError(Exception):
    """Raises an Exception if now password was set before trying to save the User model."""
    def __init__(self):
        super(PasswordValidationError, self).__init__('A password must be set before saving.')


# ========== # MODELS SCHEMA # ========== #
class User(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(default=None, max_length=255, null=False, min_length=6)
    # first_name = StringField(required=True)
    # last_name = StringField(required=True)
    username = StringField(required=True)
    # user_type = StringField(required=True, max_length=1, choices=USERS)
    active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    created = DateTimeField(default=datetime.datetime.utcnow())
    last_updated = DateTimeField(default=None)
    last_login = DateTimeField(default=None)
    # Define the collection and indexing for this document
    meta = {
        'collection': 'users',
        'indexes': [
            'last_login',
            # {'fields': ['created'], 'expireAfterSeconds': 3600},  # Time To Live index - expires from collection
            'email'
        ]
    }

    def set_password(self, raw_password: str) -> None:
        """Helper utility method to save an encrypted password using the Bcrypt Flask extension."""
        self.password = bcrypt.generate_password_hash(
            password=raw_password,
            rounds=current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def to_dict(self, *args, **kwargs) -> dict:
        """Simple Document.User helper method to get a Python dict back."""
        return {
            '_id': self.id,
            'email': self.email,
            'username': self.username,
            'created': self.created,
            'active': self.active,
            'last_updated': self.last_updated,
            'last_login': self.last_login,
        }

    # MongoEngine allows you to create custom cleaning rules for your documents when calling save().
    # By providing a custom clean() method you can do any pre validation / data cleaning.
    # This might be useful if you want to ensure a default value based on other document values.
    def clean(self):
        """Ensures a `password` has been stored before saving."""
        if self.password is None:
            raise PasswordValidationError()

        if self.last_updated is None:
            self.last_updated = self.created
