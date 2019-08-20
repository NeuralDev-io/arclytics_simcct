# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# settings.py.py
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
__date__ = '2019.08.09'
"""settings.py.py: 

{Description}
"""

import os
import sys
import json
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Load environment variables
env_path = os.path.join(BASE_DIR, '.env')
if os.path.isfile(env_path):
    load_dotenv(env_path)

APP_CONFIGS = None
DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'

DEFAULT_CONFIGS = Path(BASE_DIR) / 'configs' / 'app.json'
if os.path.isfile(DEFAULT_CONFIGS):
    with open(DEFAULT_CONFIGS) as config_file:
        APP_CONFIGS = json.load(config_file)
else:
    raise FileNotFoundError('Cannot find app.json')
