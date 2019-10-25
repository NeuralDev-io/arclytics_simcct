# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# schemas.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.09'
"""schemas.py: 

These describe the schema required for the configurations and compositions
that will be received by the simcct server as request body data. They will
be used to validate the post data is correct before adding to any DB.
"""

from bson import ObjectId
from marshmallow import (
    Schema, ValidationError, fields, validates, validate, validates_schema,
    EXCLUDE
)
from marshmallow.validate import OneOf

from sim_api.extensions.utilities import (
    DuplicateElementError, ElementSymbolInvalid, ElementInvalid,
    ElementWeightInvalid, MissingElementError
)
from simulation.periodic import PeriodicTable

Schema.TYPE_MAPPING[ObjectId] = fields.String


def not_negative(val):
    if val < 0:
        raise ValidationError('Cannot be negative.')


class SimulationResultsSchema(Schema):
    """This schema defines the full results data sent to and received from
    client.
    """
    TTT = fields.Dict()
    CCT = fields.Dict()
    USER = fields.Dict()

    # By default, `schema.load()` will raise a `ValidationError` if it
    # encounters a key with no matching `Field` in the schema
    # https://marshmallow.readthedocs.io/en/stable/quickstart.html
    # #handling-unknown-fields
    class Meta:
        unknown = EXCLUDE  # exclude unknown fields


class ElementSchema(Schema):
    symbol = fields.Str(required=True)
    weight = fields.Float(required=True)

    # By default, `schema.load()` will raise a `ValidationError` if it
    # encounters a key with no matching `Field` in the schema
    # https://marshmallow.readthedocs.io/en/stable/quickstart.html
    # #handling-unknown-fields
    class Meta:
        unknown = EXCLUDE  # exclude unknown fields

    @validates('symbol')
    def validate_symbol(self, value):
        """The validate method for the symbol field."""
        try:
            PeriodicTable[value].name
        except KeyError:
            raise ElementSymbolInvalid()
        # If the function doesn't raise an error, the check is considered passed

    # noinspection PyUnusedLocal
    @validates_schema
    def validate_carbon(self, data, **kwargs):
        # We need to make sure that the alloy cannot have a high content
        # of Carbon otherwise the simulations will raise a Math Domain Err.
        if data['symbol'] == 'C':
            if data['weight'] > 0.8:
                raise ElementWeightInvalid(
                    'Carbon weight content must not be more than 0.8'
                )

        if data['weight'] < 0:
            raise ElementWeightInvalid('Weight must be more than 0.0.')


class AlloySchema(Schema):
    _id = fields.Str()
    name = fields.Str()
    compositions = fields.List(fields.Nested(ElementSchema), required=True)

    # By default, `schema.load()` will raise a `ValidationError` if it
    # encounters a key with no matching `Field` in the schema
    # https://marshmallow.readthedocs.io/en/stable/quickstart.html
    # #handling-unknown-fields
    class Meta:
        unknown = EXCLUDE  # exclude unknown fields

    @validates('compositions')
    def validate_composition(self, value):
        # ========== # Validate for Missing Required Elements # ========== #
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
        unique_elements_set = set()
        duplicate_elements = []

        for el in value:
            if not el.get('symbol', None):
                msg = 'Field is required: ["Element.symbol"].'
                raise ElementInvalid(msg)

            if el.get('symbol', None) in valid_elements.keys():
                valid_elements[el['symbol']] = True

            # Add the element as a unique symbol in the set to check for
            # duplicates later.
            if el.get('symbol') not in unique_elements_set:
                unique_elements_set.add(el['symbol'])
            else:
                duplicate_elements.append(el['symbol'])

        # all() returns True if all values in the dict are True
        # If it does not pass, we build up a message and respond.
        if not all(el is True for el in valid_elements.values()):
            # We build up a list of missing elements for the response.
            missing_elem = []
            for k, v in valid_elements.items():
                if not v:
                    missing_elem.append(k)
            # The validation has failed so we pass the missing elements
            raise MissingElementError(f'Missing elements {missing_elem}')
        # ========== # Validate for Duplicate Elements # ========== #
        if not len(duplicate_elements) == 0:
            raise DuplicateElementError(
                f'Duplicate elements {str(duplicate_elements)}'
            )

        # The validation has succeeded


class AlloysTypeSchema(Schema):
    parent = fields.Nested(AlloySchema, allow_none=True)
    weld = fields.Nested(AlloySchema, allow_none=True)
    mix = fields.Nested(AlloySchema, allow_none=True)


class AlloyStoreSchema(Schema):
    """This is the schema that defines how the Alloy is stored in the Session
    and the User's Mongo Document.
    """
    alloy_option = fields.Str(required=True, validate=OneOf(['single', 'mix']))
    alloys = fields.Nested(AlloysTypeSchema)


class ConfigurationsSchema(Schema):
    # This defines whether a Configuration is valid or not.
    # This one is not required because we can define it later.
    is_valid = fields.Boolean(default=False, required=False)

    method = fields.Str(
        default='Li98',
        required=True,
        allow_none=False,
        data_key='method',
        validate=OneOf(['Li98', 'Kirkaldy83']),
        error_messages={
            'null': 'You must provide a method.',
            'required': 'A method is required.'
        }
    )
    grain_size = fields.Float(required=False, validate=not_negative)

    # These values should always be either False or True.
    auto_calculate_ms = fields.Boolean(default=False, required=True)
    auto_calculate_bs = fields.Boolean(default=False, required=True)
    auto_calculate_ae = fields.Boolean(default=False, required=True)

    # The parameters required for the calculations
    ms_temp = fields.Float(required=False, validate=not_negative)
    ms_rate_param = fields.Float(required=True, validate=not_negative)
    bs_temp = fields.Float(required=False, validate=not_negative)
    ae1_temp = fields.Float(required=False, validate=not_negative)
    ae3_temp = fields.Float(required=False, validate=not_negative)
    start_temp = fields.Float(required=True, validate=not_negative)

    # Validation for this done in method `validate_cooling_rate`.
    # User cooling curve configurations
    nucleation_start = fields.Float(required=False)
    nucleation_finish = fields.Float(required=False)
    cct_cooling_rate = fields.Float(required=False)

    # By default, `schema.load()` will raise a `ValidationError` if it
    # encounters a key with no matching `Field` in the schema
    # https://marshmallow.readthedocs.io/en/stable/quickstart.html
    # #handling-unknown-fields
    class Meta:
        unknown = EXCLUDE  # exclude unknown fields

    # noinspection PyUnusedLocal
    @validates_schema
    def validate_fields(self, data, **kwargs):
        if data['nucleation_start'] >= data['nucleation_finish']:
            raise ValidationError('Nucleation start must be more than finish.')

    @validates('nucleation_start')
    def validate_nucleation_start(self, value):
        if value <= 0.0:
            raise ValidationError('Nucleation start must be more than 0.0.')
        if value >= 99.99999:
            raise ValidationError(
                'Nucleation start cannot be more than 99.99.'
            )

    @validates('nucleation_finish')
    def validate_nucleation_finish(self, value):
        if value <= 0.0:
            raise ValidationError('Nucleation finish must be more than 0.0.')
        if value >= 99.99999:
            raise ValidationError(
                'Nucleation finish cannot be more than 99.99.'
            )

    @validates('cct_cooling_rate')
    def validate_cooling_rate(self, value):
        if value < 1.0:
            raise ValidationError('Cooling rate must be more than 0.')
