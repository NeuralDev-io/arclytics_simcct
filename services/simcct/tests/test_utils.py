# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_utils.py
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
__date__ = '2019.09.02'

"""test_utils.py: 

{Description}
"""

# Built-in/Generic Imports
import os


def get_mongo_uri():
    host = os.environ.get('MONGO_HOST')
    port = int(os.environ.get('MONGO_PORT'))
    username = str(os.environ.get('MONGO_APP_USER'))
    password = str(os.environ.get('MONGO_APP_USER_PASSWORD'))
    db = str(os.environ.get('MONGO_APP_DB'))
    return f'mongodb://{username}:{password}@{host}:{port}/{db}'


