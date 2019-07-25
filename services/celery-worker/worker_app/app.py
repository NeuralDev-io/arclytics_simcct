# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# app.py
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'
"""app.py:

This is the entrypoint to our Celery Worker Flask server.
"""

import datetime
import json
import os

from flask import Flask
from flask_mail import Mail

# Instantiate the Mongo object to store a connection
app_settings = os.getenv('APP_SETTINGS')
mail = Mail()


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o.isoformat())
        return json.JSONEncoder.default(self, o)


def create_app(script_info=None, configs_path=app_settings) -> Flask:
    """Create a Flask application using the app factory pattern.

    Args:
        configs_path: the path to the Configs file to build Flask from.
        script_info: any additional information from the script running.

    Returns:
        A Flask app instance.
    """

    # instantiate the application
    app = Flask(__name__)

    # Setup the configuration for Flask
    app.config.from_object(configs_path)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    # Set up Flask extensions
    mail.init_app(app)

    app.json_encoder = JSONEncoder

    return app
