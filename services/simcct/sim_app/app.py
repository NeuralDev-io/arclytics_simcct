# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# app.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.5.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""app.py:

This is the entrypoint to our SimCCT Flask API server.
"""

import os
import json
import sys
from datetime import datetime

import numpy as np
from dotenv import load_dotenv
from bson import ObjectId
from flask import Flask

from extensions import cors, api, session


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime):
            return str(o.isoformat())
        if isinstance(o, np.float):
            return str(o)
        if isinstance(o, np.float32):
            return str(o)
        if isinstance(o, np.float64):
            return str(o)
        return json.JSONEncoder.default(self, o)


# Setup the environment
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(BASE_DIR)

# Load environment variables
env_path = os.path.join(BASE_DIR, '.env')
if os.path.isfile(env_path):
    load_dotenv(env_path)

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'


def create_app(script_info=None) -> Flask:
    """Default Flask method to create a Flask app and its context. It sets
    the configurations first and then initialises the extensions to other
    required libraries to be used in the application.

    Args:
        script_info: None

    Returns:
        A Flask app object.
    """

    # Instantiate the application
    app = Flask(__name__)

    # ========== # CONFIGURATIONS # ========== #
    app_settings = os.environ.get('APP_SETTINGS', None)
    app.config.from_object(app_settings)

    # Register blueprints
    from sim_app.resources.session import session_blueprint
    app.register_blueprint(session_blueprint)
    from sim_app.resources.sim_configurations import configs_blueprint
    app.register_blueprint(configs_blueprint)
    from sim_app.resources.alloys import alloys_blueprint
    app.register_blueprint(alloys_blueprint)
    from sim_app.resources.simulation import sim_blueprint
    app.register_blueprint(sim_blueprint)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    extensions(app)

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app


def extensions(app) -> None:
    """Registers 0 or more extensions for Flask and then mutates the app
    instance passed in.

    Args:
        app: A Flask app instance.

    Returns:
        None.
    """
    api.init_app(app)
    cors.init_app(app)
    session.init_app(app)

    return None
