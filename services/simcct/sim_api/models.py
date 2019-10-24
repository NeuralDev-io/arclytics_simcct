# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# models.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '2.0.0'
__status__ = 'production'
__date__ = '2019.07.03'
"""models.py: 

This module defines the Object Document Model and schemas for the Arclytics
Sim database using MongoDB. Here we define the `mongoengine.Document` and 
`mongoengine.EmbeddedDocument` models for the Arclytics SimCCT API 
microservice.
"""

from datetime import datetime
from typing import Tuple, Union

from bson import ObjectId
from flask import current_app, json
from mongoengine import (
    BooleanField, DO_NOTHING, DateTimeField, DictField, Document, EmailField,
    EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    FloatField, IntField, ObjectIdField, ReferenceField, StringField,
    LongField, PointField, ValidationError, queryset_manager
)

from arc_logging import AppLogger
from sim_api.extensions import bcrypt
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid, JSONEncoder,
    MissingElementError, PasswordValidationError, PeriodicTable
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
    try:
        if float(val) < 0.0:
            raise ValidationError('Cannot be a negative number.')
    except ValueError:
        raise ValidationError('Value Error.')
    except TypeError:
        raise ValidationError('Type Error.')


def greater_than_zero(val):
    try:
        if float(val) < 0.0 or float(val) == 0:
            raise ValidationError('Must be more than 0.0.')
    except ValueError:
        raise ValidationError('Value Error.')
    except TypeError:
        raise ValidationError('Type Error.')


def not_over_100(val):
    try:
        if float(val) > 100.0:
            raise ValidationError('Must be less than 100.0.')
    except ValueError:
        raise ValidationError('Value Error.')
    except TypeError:
        raise ValidationError('Type Error.')


def within_percentage_bounds(val):
    try:
        if float(val) > 100.0:
            raise ValidationError('Must be less than 100.0.')
        if float(val) < 0.0:
            raise ValidationError('Must be more than 0.0.')
    except ValueError:
        raise ValidationError('Value Error.')
    except TypeError:
        raise ValidationError('Type Error.')


def validate_no_duplicate_elements(alloy_comp: list
                                   ) -> Tuple[bool, Union[set, None]]:
    elements = []
    for e in alloy_comp:
        elements.append(e['symbol'])
    duplicates = set([x for x in elements if elements.count(x) > 1])
    if len(duplicates) > 0:
        return False, duplicates
    return True, None


# ========== # EMBEDDED DOCUMENTS MODELS SCHEMA # ========== #
class UserProfile(EmbeddedDocument):
    # Decision:
    # Not adding profile photos as not required however, we can easily do so
    # by adding the following dependencies. Additionally, you must define a
    # Cloud CDN to ensure the photos are not stored in this server as per
    # best-practices and industry standards.
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
    sub_to_feedback = BooleanField(default=False)

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


class SimulationResults(EmbeddedDocument):
    # Using DictField() because it requires no validation on the internal
    # nesting but we don't really need to validate this data.

    # Comments are just to describe the schema of the data.
    # Both of these will have the following:
    # ferrite_nucleation: {"time": [], "temp": []}
    # ferrite_completion: {"time": [], "temp": []}
    # pearlite_nucleation: {"time": [], "temp": []}
    # pearlite_completion: {"time": [], "temp": []}
    # bainite_nucleation: {"time": [], "temp": []}
    # bainite_completion: {"time": [], "temp": []}
    # martensite: {"time": [], "temp": []}
    TTT = DictField()
    CCT = DictField()
    # This will have the following:
    # user_cooling_curve: {"time": [], "temp": []}
    # user_phase_fraction_data: {
    #   "austenite": [], "ferrite": [], "pearlite": [],
    #   "bainite": [], "martensite": []
    # }
    # slider_time_field: float
    # slider_temp_field: float
    # slider_max: int
    USER = DictField()

    def to_dict(self):
        return {'TTT': self.TTT, 'CCT': self.CCT, 'USER': self.USER}


class Configuration(EmbeddedDocument):
    is_valid = BooleanField(default=False, required=True, null=False)
    method = StringField(
        null=False, required=True, choices=('Li98', 'Kirkaldy83')
    )
    grain_size = FloatField(null=False, required=True, validation=not_negative)
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

    # noinspection PyMethodParameters
    @queryset_manager
    def as_dict(cls, queryset) -> list:
        """Adding an additional QuerySet context method to return a list of
        `sim_api.models.Configuration` Documents instead of a QuerySet.

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
    weight = FloatField(required=True, validation=not_negative)

    def to_dict(self):
        return {'symbol': self.symbol, 'weight': self.weight}

    def clean(self):
        """
        Ensure that the `symbol` field must conform to a proper periodic
        table element symbol and ensure they are both required.
        """
        # These ensure they are not missing.
        if not self.symbol:
            msg = 'Field is required: ["Element.symbol"]'
            raise ElementInvalid(message=msg)

        if not self.weight == 0.0:
            if not self.weight:
                msg = 'Field is required: ["Element.weight"]'
                raise ElementInvalid(message=msg)

        # Make sure they are a valid Element symbol as per the `PeriodicTable`
        try:
            valid_symbol = PeriodicTable[self.symbol].name
        except KeyError:
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

        no_duplicates, duplicate = validate_no_duplicate_elements(
            self.compositions
        )
        if not no_duplicates:
            raise DuplicateElementError(f'Duplicate element {duplicate}')

    def __str__(self):
        return self.to_json()


class AlloyType(EmbeddedDocument):
    parent = EmbeddedDocumentField(
        document_type=Alloy, default=None, null=True
    )
    weld = EmbeddedDocumentField(document_type=Alloy, default=None, null=True)
    mix = EmbeddedDocumentField(document_type=Alloy, default=None, null=True)

    def to_dict(self):
        data = {'parent': None, 'weld': None, 'mix': None}

        if self.parent is not None:
            data['parent'] = self.parent.to_dict()
        if self.weld is not None:
            data['weld'] = self.weld.to_dict()
        if self.mix is not None:
            data['mix'] = self.mix.to_dict()

        return data


class AlloyStore(EmbeddedDocument):
    alloy_option = StringField(required=True, choices=('single', 'mix'))
    alloys = EmbeddedDocumentField(document_type=AlloyType, required=True)

    def to_dict(self):
        return {
            'alloy_option': self.alloy_option,
            'alloys': self.alloys.to_dict()
        }

    def __str__(self):
        return self.to_json()


class Rating(EmbeddedDocument):
    rating = IntField(min_value=1, max_value=5, required=True)
    created_date = DateTimeField(default=datetime.utcnow(), required=True)

    def to_dict(self):
        return {'rating': self.rating, 'created_date': str(self.created_date)}


class LoginData(EmbeddedDocument):
    created_datetime = DateTimeField(default=datetime.utcnow(), required=True)
    state = StringField()
    country = StringField()
    continent = StringField()
    accuracy_radius = IntField()
    geo_point = PointField()
    timezone = StringField()
    ip_address = StringField()

    def to_dict(self):
        return {
            'created_datetime': str(self.created_datetime.isoformat()),
            'state': self.state,
            'country': self.country,
            'continent': self.continent,
            'accuracy_radius': self.accuracy_radius,
            'geo_point': self.geo_point,
            'timezone': self.timezone,
            'ip_address': self.ip_address
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
    # Note: It is necessary to use `sim_api.schemas.ConfigurationSchema`,
    # `sim_api.schemas.AlloySchema` and
    # `sim_api.schemas.SimulationResultsSchema` to validate these before
    # dumping to the database if we want to ensure validity.
    last_configuration = DictField(default=None)
    last_alloy_store = DictField(default=None)
    last_simulation_results = DictField(default=None)
    last_simulation_invalid_fields = DictField(default=None)

    # Store the number of simulations the user has run
    simulations_count = LongField(default=0)

    # Store alloys for the user
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

    ratings = EmbeddedDocumentListField(document_type=Rating)
    login_data = EmbeddedDocumentListField(document_type=LoginData)

    # Define the collection and indexing for this document
    meta = {
        'collection':
        'users',
        'indexes': [
            # This create text indexes for advanced text search
            {
                'fields': ['$first_name', '$last_name', '$email'],
                # For a text index, the weight of an indexed field denotes
                # the significance of the field relative to the other indexed
                # fields in terms of the text search score.
                # 2 times (i.e. 10:1) the impact as a term match in the
                # last_name and email fields
                # 10:9 impact as a term match in the last_name:first_name
                'weights': {
                    'last_name': 10,
                    'first_name': 9,
                    'email': 1
                }
            }
        ]
    }

    def set_password(self, raw_password: str) -> None:
        """
        Helper utility method to save an encrypted password using the
        Bcrypt Flask extension.
        """
        self.password = bcrypt.generate_password_hash(
            password=raw_password,
            rounds=current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def to_dict(self) -> dict:
        """Simple Document.User helper method to get a Python dict back."""
        last_login = None
        last_updated = None
        if self.last_login is not None:
            last_login = self.last_login.isoformat()
        if self.last_updated is not None:
            last_updated = self.last_updated.isoformat()

        # We set a default profile that we always send to the client
        profile = {
            'aim': None,
            'highest_education': None,
            'sci_tech_exp': None,
            'phase_transform_exp': None
        }
        if self.profile is not None:
            profile = self.profile.to_dict()

        user = {
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

    # MongoEngine allows you to create custom cleaning rules for your documents
    # when calling save(). By providing a custom clean() method you can do
    # any pre validation / data cleaning. This might be useful if you want to
    # ensure a default value based on other document values.
    def clean(self):
        """
        Ensures a multitude of business logic is checked before we save the
        User to the database. These include the following:
          - Password must be set by calling `new_user.set_password(raw_pw)`
          - Every time a User object is saved the `User.last_updated` datetime
            is set to the current `utcnow()` datetime.
          - Update the `User.is_admin` boolean based on other criteria.
          - By default, if there is not `User.ratings` or `User.login_data`
            we make a Python list as the default.
        """
        if self.password is None:
            raise PasswordValidationError()

        if self.last_updated is None:
            self.last_updated = self.created
        else:
            self.last_updated = datetime.utcnow()

        self.is_admin = (
            not self.disable_admin and self.admin_profile is not None
        )

        if not self.ratings:
            self.ratings = []

        if not self.login_data:
            self.login_data = []

    # noinspection PyMethodParameters
    @queryset_manager
    def as_dict(cls, queryset) -> list:
        """Adding an additional QuerySet context method to return a list of
        `sim_api.models.Users` Documents instead of a QuerySet.

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
    configurations = EmbeddedDocumentField(
        document_type=Configuration, required=True, null=False
    )
    alloy_store = EmbeddedDocumentField(
        document_type=AlloyStore, required=True, null=False
    )
    simulation_results = EmbeddedDocumentField(
        document_type=SimulationResults, required=True, null=False
    )
    created = DateTimeField(default=datetime.utcnow(), null=False)

    meta = {'collection': 'saved_simulations'}

    def to_dict(self):
        return {
            '_id': str(self.id),
            'configurations': self.configurations.to_dict(),
            'alloy_store': self.alloy_store.to_dict(),
            'created': str(self.created.isoformat()),
            'simulation_results': self.simulation_results.to_dict()
        }

    def __str__(self):
        return self.to_json()


class SharedSimulation(Document):
    owner_email = EmailField(required=True)
    created_date = DateTimeField(default=datetime.utcnow(), required=True)
    configuration = EmbeddedDocumentField(
        document_type=Configuration, required=True
    )
    alloy_store = EmbeddedDocumentField(
        document_type=AlloyStore, required=True
    )
    simulation_results = EmbeddedDocumentField(
        document_type=SimulationResults, required=True, null=False
    )

    meta = {'collection': 'shared_simulations'}

    def to_dict(self):
        return {
            'owner_email': self.owner_email,
            'created_date': str(self.created_date),
            'configurations': self.configuration.to_dict(),
            'alloy_store': self.alloy_store.to_dict(),
            'simulation_results': self.simulation_results.to_dict()
        }


class Feedback(Document):
    user = ReferenceField(User, reverse_delete_rule=DO_NOTHING)
    category = StringField(required=True)
    rating = IntField(min_value=1, max_value=5, default=None)
    comment = StringField(required=True)
    created_date = DateTimeField(
        default=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        required=True
    )

    meta = {
        'collection':
        'feedback',
        'indexes': [
            # This create text indexes for advanced text search
            {
                'fields': ['$category', '$comment'],
                # For a text index, the weight of an indexed field denotes
                # the significance of the field relative to the other indexed
                # fields in terms of the text search score.
                # 5:1 the impact as a term match in the category vs comments
                'weights': {
                    'category': 3,
                    'comment': 1
                }
            }
        ]
    }

    def to_dict(self):
        return {
            'user_email': self.user.email,
            'category': self.category,
            'rating': self.rating,
            'comment': self.comment,
            'created_date': str(self.created_date)
        }
