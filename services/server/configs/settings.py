# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# settings.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.26'

"""settings.py: 

{Description}
"""

import os
from pathlib import Path
import json

from logger.arc_logger import AppLogger

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
DEFAULT_CONFIGS = Path(BASE_DIR) / 'configs' / 'app.json'
DEFAULT_LOGGER = AppLogger('ARCLYTICS')
APP_CONFIGS = None

if os.path.isfile(DEFAULT_CONFIGS):
    with open(DEFAULT_CONFIGS) as config_file:
        APP_CONFIGS = json.load(config_file)
else:
    raise FileNotFoundError
