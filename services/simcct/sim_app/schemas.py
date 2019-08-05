# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# schemas.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.4.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""schemas.py: 

These describe the schema required for the configurations and compositions
that will be received by the simcct server as request body data. They will
be used to validate the post data is correct before adding to any DB.
"""

from bson import ObjectId
from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import OneOf
from simulation.periodic import PeriodicTable

Schema.TYPE_MAPPING[ObjectId] = fields.String


class ElementSchema(Schema):
    symbol = fields.Str(required=True)
    weight = fields.Float(required=True)

    @validates('symbol')
    def validate_symbol(self, value):
        """The validate method for the symbol field."""
        try:
            valid_symbol = PeriodicTable[value].name
        except KeyError as e:
            msg = (
                'ValidationError (Element) (Field does not match a valid '
                'element symbol in the Periodic Table: ["symbol"])'
            )
            raise ValidationError(msg)
        # If the function doesn't raise an error, the check is considered passed


class AlloySchema(Schema):
    _id = fields.Str()
    name = fields.Str()
    compositions = fields.List(fields.Nested(ElementSchema))


class AlloysTypeSchema(Schema):
    parent = fields.Nested(AlloySchema, allow_none=True)
    weld = fields.Nested(AlloySchema, allow_none=True)
    mix = fields.Nested(AlloySchema, allow_none=True)


class AlloyStoreRequestSchema(Schema):
    """This is the schema that defines the request body for changing alloys."""
    alloy_option = fields.Str(
        required=True, validate=OneOf(['single', 'both', 'mix'])
    )
    alloy_type = fields.Str(
        required=True, validate=OneOf(['parent', 'weld', 'mix'])
    )
    alloy = fields.Nested(AlloySchema, required=True)


class AlloyStoreSchema(Schema):
    """This is the schema that defines how the Alloy is stored in the Session
    and the User's Mongo Document.
    """
    alloy_option = fields.Str(
        required=True, validate=OneOf(['single', 'both', 'mix'])
    )
    alloys = fields.Nested(AlloysTypeSchema)


class ConfigurationsSchema(Schema):
    is_valid = fields.Boolean(default=False)
    method = fields.Str(
        default='Li98',
        required=True,
        allow_none=False,
        data_key='method',
        error_messages={
            'null': 'You must provide a method.',
            'required': 'A method is required.'
        }
    )
    # TODO(andrew@neuraldev.io -- Sprint 6): do error messages on all these
    grain_size = fields.Float(required=True)
    nucleation_start = fields.Float(required=True)
    nucleation_finish = fields.Float(required=True)
    auto_calculate_ms = fields.Boolean(default=False, required=True)
    ms_temp = fields.Float(required=False)
    ms_rate_param = fields.Float(required=True)
    auto_calculate_bs = fields.Boolean(default=False, required=True)
    bs_temp = fields.Float(required=False)
    auto_calculate_ae = fields.Boolean(default=False, required=True)
    ae1_temp = fields.Float(required=False)
    ae3_temp = fields.Float(required=False)
    start_temp = fields.Int(required=True)
    cct_cooling_rate = fields.Int()


class SetupConfigsSchema(Schema):
    grain_size = fields.Float()
    nucleation_start = fields.Float()
    nucleation_finish = fields.Float()
    start_temp = fields.Int()
    cct_cooling_rate = fields.Int()
