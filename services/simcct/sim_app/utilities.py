# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.07'
"""utilities.py: 

Just some helper functions for the Flask app.
"""

import os
import json
import numpy as np
from datetime import datetime

from bson import ObjectId


def get_mongo_uri():
    host = os.environ.get('MONGO_HOST')
    port = int(os.environ.get('MONGO_PORT'))
    username = str(os.environ.get('MONGO_APP_USER'))
    password = str(os.environ.get('MONGO_APP_USER_PASSWORD'))
    db = str(os.environ.get('MONGO_APP_DB'))
    return f'mongodb://{username}:{password}@{host}:{port}/{db}'


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, datetime):
            return str(o.isoformat())
        if isinstance(o, np.float):
            return str(o)
        if isinstance(o, np.float32):
            return str(o)
        if isinstance(o, np.float64):
            return str(o)
        return json.JSONEncoder.default(self, o)
