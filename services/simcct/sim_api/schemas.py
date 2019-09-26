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
from marshmallow import Schema, ValidationError, fields, validates
from marshmallow.validate import OneOf

from arc_simulation.periodic import PeriodicTable
from arc_simulation.utilities import MissingElementError

Schema.TYPE_MAPPING[ObjectId] = fields.String


class PlotData(Schema):
    temp = fields.List(fields.Float())
    time = fields.List(fields.Float())


class MainPlotSchema(Schema):
    ferrite_nucleation = fields.Nested(PlotData)
    ferrite_completion = fields.Nested(PlotData)
    pearlite_nucleation = fields.Nested(PlotData)
    pearlite_completion = fields.Nested(PlotData)
    bainite_nucleation = fields.Nested(PlotData)
    bainite_completion = fields.Nested(PlotData)
    martensite = fields.Nested(PlotData)


class PhaseFractionSchema(Schema):
    austenite = fields.List(fields.Float())
    ferrite = fields.List(fields.Float())
    pearlite = fields.List(fields.Float())
    bainite = fields.List(fields.Float())
    martensite = fields.List(fields.Float())


class UserCoolingProfileSchema(Schema):
    user_cooling_curve = fields.Nested(PlotData)
    user_phase_fraction_data = fields.Nested(PhaseFractionSchema)
    slider_time_field = fields.Float()
    slider_temp_field = fields.Float()
    slider_max = fields.Int()


class SimulationResultsSchema(Schema):
    """This schema defines the full results data sent to and received from
    client.
    """
    TTT = fields.Nested(MainPlotSchema)
    CCT = fields.Nested(MainPlotSchema)
    USER = fields.Nested(UserCoolingProfileSchema)


class ElementSchema(Schema):
    symbol = fields.Str(required=True)
    weight = fields.Float(required=True)

    @validates('symbol')
    def validate_symbol(self, value):
        """The validate method for the symbol field."""
        try:
            PeriodicTable[value].name
        except KeyError:
            msg = (
                'ValidationError (Element) (Field does not match a valid '
                'element symbol in the Periodic Table: ["symbol"])'
            )
            raise ValidationError(msg)
        # If the function doesn't raise an error, the check is considered passed


class AlloySchema(Schema):
    _id = fields.Str()
    name = fields.Str()
    compositions = fields.List(fields.Nested(ElementSchema), required=True)

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
            if not el.get('symbol', None):
                msg = 'Missing data for required field ["symbol"].'
                raise ValidationError(msg)

            if el.get('symbol', None) in valid_elements.keys():
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
    alloy_option = fields.Str(required=True, validate=OneOf(['single', 'mix']))
    alloy_type = fields.Str(
        required=True, validate=OneOf(['parent', 'weld', 'mix'])
    )
    alloy = fields.Nested(AlloySchema, required=True)


class AlloyStoreSchema(Schema):
    """This is the schema that defines how the Alloy is stored in the Session
    and the User's Mongo Document.
    """
    alloy_option = fields.Str(required=True, validate=OneOf(['single', 'mix']))
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
