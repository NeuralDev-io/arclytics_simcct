# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# settings.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.26'
"""settings.py: 

{Description}
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

APP_CONFIGS = None
DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'

DEFAULT_CONFIGS = Path(BASE_DIR) / 'configs' / 'app.json'
if os.path.isfile(DEFAULT_CONFIGS):
    with open(DEFAULT_CONFIGS) as config_file:
        APP_CONFIGS = json.load(config_file)
else:
    raise FileNotFoundError('Cannot find app.json')