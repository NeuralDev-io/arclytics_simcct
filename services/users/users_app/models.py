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
from datetime import datetime, timedelta
from typing import Union, Tuple

from bson import ObjectId
from mongoengine import (
    Document, EmbeddedDocument, StringField, EmailField, BooleanField,
    DateTimeField, EmbeddedDocumentField, IntField, FloatField, DO_NOTHING,
    EmbeddedDocumentListField, queryset_manager, ObjectIdField, ReferenceField,
    ValidationError
)
from flask import current_app, json

from logger.arc_logger import AppLogger
from users_app.extensions import bcrypt
from users_app.utilities import (
    JSONEncoder, PeriodicTable, PasswordValidationError, ElementSymbolInvalid,
    ElementInvalid, MissingElementError
)

logger = AppLogger(__name__)


# ========== # FIELD CUSTOM VALIDATION # ========== #
def validate_comp_elements(alloy_comp: list) -> Tuple[bool, list]:
    """We validate the alloy has all the elements that will be needed by the
    simulation algorithms using a hashed dictionary as it is much faster.

    Args:
        alloy_comp: a list of Alloy composition objects (i.e.
                    {"symbol": "C", "weight": 1.0})

    Returns:
        A tuple response whether the validation succeeded and the missing
        elements if it did not.
    """
    valid_elements = {
        'C': False,
        'Mn': False,
        'Ni': False,
        'Cr': False,
        'Mo': False,
        'Si': False,
        'Co': False,
        'W': False,
        'As': False,
        'Fe': False
    }

    for el in alloy_comp:
        if el['symbol'] in valid_elements.keys():
            valid_elements[el['symbol']] = True

    # all() returns True if all values in the dict are True
    # If it does not pass, we build up a message and respond.
    if not all(el is True for el in valid_elements.values()):
        # We build up a list of missing elements for the response.
        missing_elem = []
        for k, v in valid_elements.items():
            if not v:
                missing_elem.append(k)
        # The validation has failed so we return False and the missing elements
        return False, missing_elem
    # The validation has succeeded
    return True, []


def not_negative(val):
    if val < 0.0:
        raise ValidationError('Cannot be a negative number.')


def greater_than_zero(val):
    if val < 0.0 or val == 0:
        raise ValidationError('Must be more than 0.0.')


def not_over_100(val):
    if val > 100.0:
        raise ValidationError('Must be less than 100.0.')


def within_percentage_bounds(val):
    if val > 100.0:
        raise ValidationError('Must be less than 100.0.')
    if val < 0.0:
        raise ValidationError('Must be more than 0.0.')


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
        required=True,
        default=None,
        null=True
    )
    highest_education = StringField(
        help_text='What is the highest level of education have you studied?',
        required=True,
        default=None,
        null=True
    )
    sci_tech_exp = StringField(
        help_text='What is your experience with scientific software?',
        required=True,
        default=None,
        null=True
    )
    phase_transform_exp = StringField(
        help_text=(
            'What is your experience with solid-state phase '
            'transformation?'
        ),
        required=True,
        default=None,
        null=True
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
    verified = BooleanField(default=False)
    promoted_by = ObjectIdField()

    def to_dict(self) -> dict:
        """
        Simple EmbeddedDocument.AdminProfile helper method to get a
        Python dict back.
        """
        return {
            'position': self.position,
            'mobile_number': self.mobile_number,
            'verified': self.verified
        }


# TODO(andrew@neuraldev.io): Add these
class SimulationResults(EmbeddedDocument):
    pass


class Configuration(EmbeddedDocument):
    is_valid = BooleanField(default=False, required=True, null=False)
    method = StringField(
        null=False, required=True, choices=('Li98', 'Kirkaldy83')
    )
    grain_size = FloatField(
        null=False, required=True, validation=not_negative
    )
    nucleation_start = FloatField(
        null=False, required=True, validation=within_percentage_bounds
    )
    nucleation_finish = FloatField(
        null=False, required=True, validation=within_percentage_bounds
    )
    auto_calculate_ms = BooleanField(default=True, null=False, required=True)
    auto_calculate_bs = BooleanField(default=True, null=False, required=True)
    auto_calculate_ae = BooleanField(default=True, null=False, required=True)
    ms_temp = FloatField(
        default=0.0, null=False, required=True, validation=not_negative
    )
    ms_rate_param = FloatField(
        default=0.0, null=False, required=True, validation=not_negative
    )
    bs_temp = FloatField(
        default=0.0, null=False, required=True, validation=not_negative
    )
    ae1_temp = FloatField(
        default=0.0, null=False, required=True, validation=not_negative
    )
    ae3_temp = FloatField(
        default=0.0, null=False, required=True, validation=not_negative
    )
    start_temp = IntField(
        default=900, null=False, required=True, validation=not_negative
    )
    cct_cooling_rate = IntField(
        default=10, null=False, required=True, validation=not_negative
    )

    def to_dict(self) -> dict:
        """
        Simple EmbeddedDocument.Configuration helper method to get a Python dict
        """
        return {
            'is_valid': self.is_valid,
            'method': self.method,
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
    symbol = StringField(max_length=2, required=True)
    weight = FloatField(required=True)

    def to_dict(self):
        return {'symbol': self.symbol, 'weight': self.weight}

    def clean(self):
        """Ensure that the `symbol` field must conform to a proper periodic
        table element symbol and ensure they are both required.
        """
        # These ensure they are not missing.
        if not self.symbol:
            msg = 'symbol.Field is required: ["Element.symbol"])'
            raise ElementInvalid(message=msg)

        if not self.weight == 0.0:
            if not self.weight:
                msg = 'symbol.Field is required: ["Element.weight"]'
                raise ElementInvalid(message=msg)

        try:
            valid_symbol = PeriodicTable[self.symbol].name
        except KeyError as e:
            raise ElementSymbolInvalid()
        self.symbol = valid_symbol

    def __str__(self):
        return self.to_json()


class Alloy(EmbeddedDocument):
    oid = ObjectIdField(default=lambda: ObjectId(), primary_key=True)
    name = StringField()
    compositions = EmbeddedDocumentListField(Element)

    def to_dict(self):
        comp = [obj.to_dict() for obj in self.compositions]
        return {'_id': str(self.oid), 'name': self.name, 'compositions': comp}

    def clean(self):
        # comps = [el for el in self.compositions]
        valid, missing = validate_comp_elements(self.compositions)
        if not valid:
            raise MissingElementError(f'Missing elements {missing}')

    def __str__(self):
        return self.to_json()


class AlloyType(EmbeddedDocument):
    parent = EmbeddedDocumentField(
        document_type=Alloy, default=None, null=True
    )
    weld = EmbeddedDocumentField(document_type=Alloy, default=None, null=True)
    mix = EmbeddedDocumentField(document_type=Alloy, default=None, null=True)

    def to_dict(self):
        data = {
            'parent': None,
            'weld': None,
            'mix': None
        }

        if self.parent is not None:
            data['parent'] = self.parent.to_dict()
        if self.weld is not None:
            data['weld'] = self.weld.to_dict()
        if self.mix is not None:
            data['mix'] = self.mix.to_dict()

        return data


class AlloyStore(EmbeddedDocument):
    alloy_option = StringField(required=True, choices=('parent', 'both', 'mix'))
    alloys = EmbeddedDocumentField(document_type=AlloyType, required=True)

    def to_dict(self):
        return {
            'alloy_option': self.alloy_option,
            'alloys': self.alloys.to_dict()
        }


# ========== # DOCUMENTS MODELS SCHEMA # ========== #
class User(Document):
    # The following fields describe the attributes of a user
    email = EmailField(required=True, unique=True)
    password = StringField(
        default=None, max_length=64, null=False, min_length=6
    )
    first_name = StringField(required=True, max_length=255)
    last_name = StringField(required=True, max_length=255)
    profile = EmbeddedDocumentField(document_type=UserProfile, default=None)
    admin_profile = EmbeddedDocumentField(
        document_type=AdminProfile, default=None
    )

    # The following fields describe the simulation properties saved to a users
    # Document for later retrieval
    last_configuration = EmbeddedDocumentField(
        document_type=Configuration, default=None
    )

    last_alloy_store = EmbeddedDocumentField(
        document_type=AlloyStore, default=None
    )

    saved_alloys = EmbeddedDocumentListField(document_type=Alloy)

    # Some rather useful metadata information that's not core to the
    # definition of a user
    active = BooleanField(default=True)
    is_admin = BooleanField(default=False, db_field='admin')
    disable_admin = BooleanField(default=False)
    verified = BooleanField(default=False)
    # Make sure when converting these that it follows ISO8601 format as
    # defined in settings.DATETIME_FMT
    created = DateTimeField(default=datetime.utcnow(), null=False)
    last_updated = DateTimeField(default=None, null=False)
    last_login = DateTimeField()

    # Define the collection and indexing for this document
    meta = {
        'collection': 'users',
        # 'indexes': [
        # {'fields': ['saved_alloys.name'], 'unique': True}
        # ]
    }

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

    @staticmethod
    def encode_password_reset_token(user_id: ObjectId) -> Union[bytes, None]:
        """Encode a timed JWT token of 30 minutes to send to the client-side
        so we can verify which user has requested to reset their password.

        Args:
            user_id: the valid ObjectId user id.

        Returns:
            A valid JWT token or None if there is any kind of generic exception.
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=30),
                'iat': datetime.utcnow(),
                'sub': user_id
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
    def decode_password_reset_token(auth_token: bytes) -> Union[ObjectId, str]:
        """Decodes the JWT auth token for the password reset.

        Args:
            auth_token: a bytes type that was encoded by

        Returns:
            An ObjectId or string.
        """
        try:
            payload = jwt.decode(
                jwt=auth_token, key=current_app.config.get('SECRET_KEY', None)
            )
            return ObjectId(payload['sub'])
        except jwt.ExpiredSignatureError as e:
            # logger.error('Signature expired error.')
            return 'Signature expired. Please get a new token.'
        except jwt.InvalidTokenError as e:
            # logger.error('Invalid token error.')
            return 'Invalid token. Please get a new token.'

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

        self.is_admin = (
            not self.disable_admin and self.admin_profile is not None
        )

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


class SavedSimulation(Document):
    user = ReferenceField(User, reverse_delete_rule=DO_NOTHING)
    configuration = EmbeddedDocumentField(
        document_type=Configuration, required=True, null=False
    )
    alloy_store = EmbeddedDocumentField(
        document_type=AlloyStore, required=True, null=False
    )
    # results = EmbeddedDocumentField(
    #     document_type=SimulationResults, required=True, null=False
    # )
    created = DateTimeField(default=datetime.utcnow(), null=False)

    meta = {'collection': 'saved_simulations'}

    # def clean(self):
    #     pass

    # def to_dict(self):
    #     pass

    # def to_json(self, *args, **kwargs):
    #     pass

    def __str__(self):
        return self.to_json()


class SharedConfiguration(Document):
    owner = EmailField(required=True)
    shared_date = DateTimeField()
    configuration = EmbeddedDocumentField(document_type=Configuration)
    # alloy_store = EmbeddedDocumentField(document_type=AlloyStore)
