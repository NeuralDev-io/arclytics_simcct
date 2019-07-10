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

from marshmallow import Schema, fields, EXCLUDE


class AlloyOption(enum.Enum):
    parent = 1
    weld = 2
    mix = 3


class SimMethod(Schema):
    li98 = fields.Boolean(attribute='li89', default=True, required=True)
    kirkaldy83 = fields.Boolean(attribute='kirkaldy83', default=False,
                                required=True)


class SimAlloy(Schema):
    parent = fields.Constant('parent')


class ConfigurationsSchema(Schema):
    method = fields.Dict(keys=fields.Str(), values=fields.Str(),
                         error_messages={'null': 'You must provide a method.',
                                         'required': 'A method is required.'},
                         data_key='method', required=True)

    class Meta:
        # By default, load will raise a ValidationError if it encounters a key
        # with no matching Field in the schema.
        # MODIFIED BEHAVIOUR:
        #  - EXCLUDE: exclude unknown fields
        #  - INCLUDE: accept and include the unknown fields
        #  - RAISE: Raise a validationError if there are any
        unknown = EXCLUDE
