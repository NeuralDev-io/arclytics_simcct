# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# settings.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.26'
"""settings.py: 

{Description}
"""

import os
import sys
import json
from pathlib import Path

from dotenv import load_dotenv

from logger.arc_logger import AppLogger

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(BASE_DIR)

ENV_CONFIGS = os.path.join(BASE_DIR, '.env')
if os.path.isfile(ENV_CONFIGS):
    load_dotenv(ENV_CONFIGS)
else:
    raise FileNotFoundError('Cannot find .env file.')

DEFAULT_LOGGER = AppLogger('ARCLYTICS')
APP_CONFIGS = None

DEFAULT_CONFIGS = Path(BASE_DIR) / 'configs' / 'app.json'
if os.path.isfile(DEFAULT_CONFIGS):
    with open(DEFAULT_CONFIGS) as config_file:
        APP_CONFIGS = json.load(config_file)
else:
    raise FileNotFoundError('Cannot find app.json')
