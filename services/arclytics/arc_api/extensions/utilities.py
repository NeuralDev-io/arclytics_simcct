# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '2.0.0'
__status__ = 'production'
__date__ = '2019.10.02'
"""utilities.py: 

Utilities for extensions that are not clearly defined.
"""

import decimal
import json
from datetime import datetime

import numpy as np
from bson import ObjectId

API_TOKEN_NAME = 'JWT_TOKEN'


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
        if isinstance(o, np.int):
            return int(o)
        if isinstance(o, np.int16):
            return int(o)
        if isinstance(o, np.int32):
            return int(o)
        if isinstance(o, np.int64):
            return int(o)
        if isinstance(o, np.float):
            return str(o)
        if isinstance(o, np.float64):
            return str(o)
        if isinstance(o, np.float64):
            return str(o)
        if isinstance(o, decimal.Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)
