# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_configurations.py
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
__date__ = '2019.07.13'
"""sim_configurations.py: 

This module deals with all the endpoints for setting and updating the 
configurations for the main simulations page. 
"""

from marshmallow import ValidationError
from flask import Blueprint, session, request
from flask_restful import Resource

configurations_blueprint = Blueprint('configurations', __name__)


