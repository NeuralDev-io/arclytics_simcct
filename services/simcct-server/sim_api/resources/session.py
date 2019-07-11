# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# session.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.10'
"""session.py: 

This module defines the resources for session management. 
"""

from flask import Blueprint, session
from flask_restful import Resource

session_blueprint = Blueprint('session', __name__)


class SessionPing(Resource):

    def get(self):
        session['redis_test'] = {
            'Test': ['This should save a value', 'Another value'],
            'Test2': 'A third value'
        }
        res = {
            'Session ID': session.sid,
            'Redis Store': session['redis_test']
        }
        return res, 200
