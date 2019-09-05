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

from flask import Flask

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'

# TODO(andrew@neuraldev.io) DO NOT TOUCH!!!!!!!!!!!!!!!!!!

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
    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects

    # ========== # INIT FLASK EXTENSIONS # ========== #
    extensions(app)

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
    return None
