# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""utilities.py: 

{Description}
"""

import datetime
import decimal
import json
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o.isoformat())
        if isinstance(o, decimal.Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)
