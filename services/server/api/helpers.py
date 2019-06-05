# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# helpers.py
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
__date__ = '2019.06.05'

"""helpers.py: 

Helper functions for user management subsystem
"""

import bcrypt
from api.app import users


def user_exist(username):
    return False if users.find({'Username', username}).count() == 0 else True


def verify_user(username, password):
    if not user_exist(username):
        return False

    user_hashed_pw = users.find({'Username': username})[0]['Password']

    if bcrypt.checkpw(password.encode('utf8'), user_hashed_pw):
        return True
    else:
        return False
