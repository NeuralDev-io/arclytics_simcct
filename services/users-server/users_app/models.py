# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# models.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.3.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""models.py: 

This module stores the mongoengine.Document models for the Arclytics API Users
microservice.
"""

import jwt
from datetime import datetime, tzinfo, timedelta
from typing import Union, Optional

from bson import ObjectId
from mongoengine import (
    Document, EmbeddedDocument, StringField, EmailField, BooleanField,
    DateTimeField, EmbeddedDocumentField, IntField, FloatField, ListField,
    EmbeddedDocumentListField, queryset_manager
)
from flask import current_app, json

from logger.arc_logger import AppLogger
from users_app import bcrypt, JSONEncoder

logger = AppLogger(__name__)
# User type choices
USERS = (('1', 'ADMIN'), ('2', 'USER'))


# ========== # UTILITIES # ========== #
# TODO(andrew@neuraldev.io): move these to a separate file at some point.
class PasswordValidationError(Exception):
    """
    Raises an Exception if now password was set before trying to save
    the User model.
    """

    def __init__(self):
        super(PasswordValidationError,
              self).__init__('A password must be set before saving.')


class SimpleUTC(tzinfo):
    def tzname(self, dt: Optional[datetime]) -> Optional[str]:
        return 'UTC'

    def utcoffset(self, dt: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)


# ========== # EMBEDDED DOCUMENTS MODELS SCHEMA # ========== #


class UserProfile(EmbeddedDocument):
    # Not having this for now until we can figure out where to store the photos
    # TODO(andrew@neuraldev.io): Uncomment Pillow dependencies Dockerfile to use
    #  and install Pillow==6.1.0
    # profile_photo = ImageField(
    #     required=False,
    #     size=(800, 600, True),
    #     thumbnail_size=(300, 300, True),
    #     help_text='Please provide a photo of 800x600 pixels only.'
    # )
    aim = StringField(
        help_text='What sentence best describes you?',
        required=False,
        default=None
    )
    highest_education = StringField(
        help_text='What is the highest level of education have you studied?',
        required=False,
        default=None
    )
    sci_tech_exp = StringField(
        help_text='What is your experience with scientific software?',
        required=False,
        default=None
    )
    phase_transform_exp = StringField(
        help_text=(
            'What is your experience with solid-state phase '
            'transformation?'
        ),
        required=False,
        default=None
    )

    def to_dict(self) -> dict:
        """
        Simple EmbeddedDocument.UserProfile helper method to get a Python dict
        back.
        """
        return {
            'aim': self.aim,
            'highest_education': self.highest_education,
            'sci_tech_exp': self.sci_tech_exp,
            'phase_transform_exp': self.phase_transform_exp
        }


class AdminProfile(EmbeddedDocument):
    position = StringField(max_length=255, required=True)
    mobile_number = StringField(max_length=11, min_length=10)

    def to_dict(self) -> dict:
        """
        Simple EmbeddedDocument.AdminProfile helper method to get a
        Python dict back.
        """
        return {'position': self.position, 'mobile_number': self.mobile_number}


class Configuration(EmbeddedDocument):
    is_valid = BooleanField()
    method = StringField(default='Li98')
    alloy_type = StringField(default='parent')
    grain_size = FloatField(default=0.0)
    nucleation_start = FloatField(default=1.0)
    nucleation_finish = FloatField(default=99.9)
    auto_calculate_ms = BooleanField(default=False)
    ms_temp = FloatField()
    ms_rate_param = FloatField()
    auto_calculate_bs = BooleanField(default=False)
    bs_temp = FloatField()
    auto_calculate_ae = BooleanField(default=False)
    ae1_temp = FloatField()
    ae3_temp = FloatField()
    start_temp = FloatField()
    cct_cooling_rate = IntField()

    def to_dict(self) -> dict:
        """
        Simple EmbeddedDocument.Configuration helper method to get a Python dict
        """
        return {
            'is_valid': self.is_valid,
            'method': self.method,
            'alloy_type': self.alloy_type,
            'grain_size': self.grain_size,
            'nucleation_start': self.nucleation_start,
            'nucleation_finish': self.nucleation_finish,
            'auto_calculate_ms': self.auto_calculate_ms,
            'auto_calculate_bs': self.auto_calculate_bs,
            'auto_calculate_ae': self.auto_calculate_ae,
            'ms_temp': self.ms_temp,
            'ms_rate_param': self.ms_rate_param,
            'bs_temp': self.bs_temp,
            'ae1_temp': self.ae1_temp,
            'ae3_temp': self.ae3_temp,
            'start_temp': self.start_temp,
            'cct_cooling_rate': self.cct_cooling_rate
        }

    @queryset_manager
    def as_dict(cls, queryset) -> list:
        """Adding an additional QuerySet context method to return a list of
        `users_app.models.Configuration` Documents instead of a QuerySet.

        Usage:
            config_list = Configuration.as_dict()

        Args:
            queryset: the queryset that must is accepted as part of the Mongo
                      BSON parameter.

        Returns:
            A list with every Configuration Document object converted to dict.
        """
        return [obj.to_dict() for obj in queryset]

    def __str__(self):
        return self.to_json()


class Element(EmbeddedDocument):
    symbol = StringField(max_length=2)
    weight = FloatField()

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'weight': self.weight
        }

    def __str__(self):
        return self.to_json()


class Compositions(EmbeddedDocument):
    comp = ListField(EmbeddedDocumentField(Element))

    def __str__(self):
        return self.to_json()


# ========== # DOCUMENTS MODELS SCHEMA # ========== #
class User(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(
        default=None, max_length=64, null=False, min_length=6
    )
    first_name = StringField(required=True, max_length=255)
    last_name = StringField(required=True, max_length=255)
    user_type = StringField(
        required=False,
        max_length=1,
        null=False,
        choices=USERS,
        default=USERS[1][0]
    )
    profile = EmbeddedDocumentField(document_type=UserProfile)
    admin_profile = EmbeddedDocumentField(document_type=AdminProfile)

    last_configuration = EmbeddedDocumentField(document_type=Configuration)
    last_compositions = EmbeddedDocumentField(document_type=Compositions)

    # TODO(andrew@neuraldev.io -- Sprint 6): Make these
    # saved_configurations = EmbeddedDocumentListField(
    # document_type=Configurations)
    # saved_compositions = EmbeddedDocumentListField(document_type=Compositions)

    # Some rather useful metadata information that's not core to the
    # definition of a user
    active = BooleanField(default=True)
    is_admin = BooleanField(default=False, db_field='admin')
    verified = BooleanField(default=False)
    # Make sure when converting these that it follows ISO8601 format as
    # defined in settings.DATETIME_FMT
    created = DateTimeField(default=datetime.utcnow(), null=False)
    last_updated = DateTimeField(default=None, null=False)
    last_login = DateTimeField()
    # Define the collection and indexing for this document
    meta = {'collection': 'users'}

    def set_password(self, raw_password: str) -> None:
        """Helper utility method to save an encrypted password using the
        Bcrypt Flask extension.
        """
        self.password = bcrypt.generate_password_hash(
            password=raw_password,
            rounds=current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    # TODO(andrew@neuraldev.io): Implement one of these just for the Profile
    #  and another one for all user details.
    def to_dict(self) -> dict:
        """Simple Document.User helper method to get a Python dict back."""
        last_login = None
        last_updated = None
        if self.last_login is not None:
            last_login = self.last_login.isoformat()
        if self.last_updated is not None:
            last_updated = self.last_updated.isoformat()
        profile = None
        if self.profile is not None:
            profile = self.profile.to_dict()

        user = {
            '_id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'active': self.active,
            'admin': self.is_admin,
            'verified': self.verified,
            'last_updated': str(last_updated),
            'created': str(self.created.isoformat()),
            'last_login': str(last_login),
            'profile': profile
        }

        if self.admin_profile is not None:
            user['admin_profile'] = self.admin_profile.to_dict()

        return user

    def to_json(self, *args, **kwargs):
        """
        Override the default method to customise the way a JSON format is
        transformed.
        """
        return json.dumps(self.to_dict(), cls=JSONEncoder)

    @staticmethod
    def encode_auth_token(user_id: ObjectId) -> Union[bytes, None]:
        """Generates JWT auth token that is returned as bytes."""
        try:
            payload = {
                'exp':
                datetime.utcnow() + timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS', 0),
                    seconds=current_app.config.
                    get('TOKEN_EXPIRATION_SECONDS', 0)
                ),
                'iat':
                datetime.utcnow(),
                'sub':
                user_id
            }

            return jwt.encode(
                payload=payload,
                key=current_app.config.get('SECRET_KEY', None),
                algorithm='HS256',
                json_encoder=JSONEncoder
            )
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
            payload = jwt.decode(
                jwt=auth_token, key=current_app.config.get('SECRET_KEY', None)
            )
            return ObjectId(payload['sub'])
        except jwt.ExpiredSignatureError as e:
            # logger.error('Signature expired error.')
            return 'Signature expired. Please login again.'
        except jwt.InvalidTokenError as e:
            # logger.error('Invalid token error.')
            return 'Invalid token. Please log in again.'

    # MongoEngine allows you to create custom cleaning rules for your documents
    # when calling save(). By providing a custom clean() method you can do
    # any pre validation / data cleaning. This might be useful if you want to
    # ensure a default value based on other document values.
    def clean(self):
        """Ensures a `password` has been stored before saving."""
        if self.password is None:
            raise PasswordValidationError()

        if self.last_updated is None:
            self.last_updated = self.created
        else:
            self.last_updated = datetime.utcnow()

    @queryset_manager
    def as_dict(cls, queryset) -> list:
        """Adding an additional QuerySet context method to return a list of
        `users_app.models.Users` Documents instead of a QuerySet.

        Usage:
            users_list = User.as_dict()

        Args:
            queryset: the queryset that must is accepted as part of the Mongo
                      BSON parameter.

        Returns:
            A list with every Users Document object converted to dict.
        """
        return [obj.to_dict() for obj in queryset]

    def __str__(self):
        return self.to_json()
