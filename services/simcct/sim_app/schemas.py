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
__version__ = '0.3.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""schemas.py: 

These describe the schema required for the configurations and compositions
that will be received by the simcct server as request body data. They will
be used to validate the post data is correct before adding to any DB.
"""

import enum

from bson import ObjectId
from marshmallow import Schema, fields

Schema.TYPE_MAPPING[ObjectId] = fields.String


class AlloyOption(enum.Enum):
    parent = 1
    weld = 2
    mix = 3


class ElementSchema(Schema):
    symbol = fields.Str(required=True)
    weight = fields.Float(required=True)


class AlloySchema(Schema):
    _id = fields.Str()
    name = fields.Str(required=True)
    compositions = fields.List(fields.Nested(ElementSchema), required=True)


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
    alloy_type = fields.Str(
        default=AlloyOption.parent.name,
        required=True,
        allow_none=False,
        data_key='alloy_type',
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

    class Meta:
        # TODO(andrew@neuraldev.io): Figure out what to do with these?
        # By default, load will raise a ValidationError if it encounters a key
        # with no matching Field in the schema.
        # MODIFIED BEHAVIOUR:
        #  - EXCLUDE: exclude unknown fields
        #  - INCLUDE: accept and include the unknown fields
        #  - RAISE: Raise a validationError if there are any
        # unknown = EXCLUDE
        pass


class NonLimitConfigsSchema(Schema):
    grain_size = fields.Float(required=True)
    nucleation_start = fields.Float(required=True)
    nucleation_finish = fields.Float(required=True)
    start_temp = fields.Int(required=True)
    cct_cooling_rate = fields.Int(required=True)
