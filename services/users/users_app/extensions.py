# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# extensions.py
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
"""extensions.py: 

{Description}
"""

from flask_cors import CORS
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_restful import Api

# Some other extensions to Flask
cors = CORS()
bcrypt = Bcrypt()
ma = Marshmallow()
api = Api()
