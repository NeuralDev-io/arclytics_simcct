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
    name = fields.Str(required=True)
    symbol = fields.Str(required=True)
    weight = fields.Float(required=True)


class AlloySchema(Schema):
    _id = fields.Str()
    name = fields.Str(required=True)
    compositions = fields.List(fields.Nested(ElementSchema), required=True)


# TODO(andrew@neuraldev.io -- soon): Change this to Alloy Schema
class CompositionSchema(Schema):
    comp = fields.List(fields.Nested(ElementSchema), required=True)


class ConfigurationsSchema(Schema):
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
    alloy = fields.Str(
        default=AlloyOption.parent.name,
        required=True,
        allow_none=False,
        data_key='alloy',
        error_messages={
            'null': 'You must provide a method.',
            'required': 'A method is required.'
        }
    )
    # TODO(andrew@neuraldev.io -- Sprint 6): do error messages on all these
    grain_size_type = fields.Str(required=True, default='ASTM')
    grain_size = fields.Float(required=True)
    nucleation_start = fields.Float(required=True)
    nucleation_finish = fields.Float(required=True)
    auto_calculate_xfe = fields.Boolean(default=False, required=True)
    xfe_value = fields.Float(required=False)
    cf_value = fields.Float(required=False)
    ceut_value = fields.Float(required=False)
    auto_calculate_ms_bs = fields.Boolean(default=False, required=True)
    transformation_method = fields.Str(
        default='Li98',
        required=True,
        allow_none=False,
        data_key='transformation_method',
        error_messages={
            'null': 'A method must be provided to calculate MS and BS.',
            'required': 'A method is required to calculate MS and BS.'
        }
    )
    ms_temp = fields.Float(required=False)
    ms_undercool = fields.Float(required=False)
    bs_temp = fields.Float(required=False)
    auto_calculate_ae = fields.Boolean(default=False, required=True)
    ae1_temp = fields.Float(required=False)
    ae3_temp = fields.Float(required=False)
    start_temp = fields.Int()
    cct_cooling_rate = fields.Int()

    class Meta:
        # By default, load will raise a ValidationError if it encounters a key
        # with no matching Field in the schema.
        # MODIFIED BEHAVIOUR:
        #  - EXCLUDE: exclude unknown fields
        #  - INCLUDE: accept and include the unknown fields
        #  - RAISE: Raise a validationError if there are any
        # unknown = EXCLUDE
        pass
