# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# schema.py
# 
# Attributions: 
# [1] 
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.09'
"""schema.py: 

{Description}
"""

import enum

from marshmallow import Schema, fields


class AlloyOption(enum.Enum):
    parent = 1
    weld = 2
    mix = 3


class ElementSchema(Schema):
    name = fields.Str(required=True)
    symbol = fields.Str(required=True)
    value = fields.Decimal(required=True)


class CompositionSchema(Schema):
    compositions = fields.List(fields.Nested(ElementSchema), required=True)


class ConfigurationsSchema(Schema):
    method = fields.Str(default='li98',
                        required=True,
                        allow_none=False,
                        data_key='method',
                        error_messages={'null': 'You must provide a method.',
                                        'required': 'A method is required.'})
    alloy = fields.Str(default=AlloyOption.parent.name,
                       required=True,
                       allow_none=False,
                       data_key='alloy',
                       error_messages={'null': 'You must provide a method.',
                                       'required': 'A method is required.'})
    # TODO(andrew@neuraldev.io -- Sprint 6): do error messages on all these
    grain_size_type = fields.Str(required=True, default='ASTM')
    grain_size = fields.Float(required=True)
    nucleation_start = fields.Float(required=True)
    nucleation_finish = fields.Float(required=True)
    auto_calculate_xfe = fields.Boolean(default=True, required=True)
    xfe_value = fields.Float(required=True)
    cf_value = fields.Float(required=True)
    ceut_value = fields.Float(required=True)
    auto_calculate_ms_bs = fields.Boolean(default=True, required=True)
    ms_temp = fields.Float(required=True)
    ms_undercool = fields.Float(required=True)
    bs_temp = fields.Float(required=True)
    auto_calculate_ae = fields.Boolean(default=True, required=True)
    ae1_temp = fields.Decimal(required=True)
    ae3_temp = fields.Decimal(required=True)
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
