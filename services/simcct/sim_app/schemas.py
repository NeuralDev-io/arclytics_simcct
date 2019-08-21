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
from simulation.utilities import MissingElementError

Schema.TYPE_MAPPING[ObjectId] = fields.String


class PlotData(Schema):
    temp = fields.List(fields.Float())
    time = fields.List(fields.Float())


class TTTSchema(Schema):
    ferrite_nucleation = fields.Nested(PlotData)
    pearlite_nucleation = fields.Nested(PlotData)


class SimulationResultsSchema(Schema):
    TTT = fields.Dict()
    CCT = fields.Dict()
    USER = fields.Dict()


class ElementSchema(Schema):
    symbol = fields.Str(required=True)
    weight = fields.Float(required=True)

    @validates('symbol')
    def validate_symbol(self, value):
        """The validate method for the symbol field."""
        try:
            PeriodicTable[value].name
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

    @validates('compositions')
    def validate_required_elements(self, value):
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

        for el in value:
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
            # The validation has failed so we pass the missing elements
            raise MissingElementError(f'Missing elements {missing_elem}')
        # The validation has succeeded


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
