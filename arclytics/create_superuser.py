# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_simc_api
# create_superuser.py
#
# Attributions:
# [1] https://gist.github.com/kelvinn/a34581ea18894e22b3a8
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'NeuralDev'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.04.06'

"""create_superuser.py: 

Python script to create a default Django superuser to make it easier for everyone to just run this.
"""

import os
import sys

import django

# First, add the project to PATH. Adjust as needed.
PWD = os.path.dirname(os.path.abspath(__file__))
print(PWD)
PROJECT_PATH = os.path.abspath(os.path.join(PWD, '../'))
sys.path.append(PROJECT_PATH)
print(PROJECT_PATH)

# Second, configure this script to use Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arclytics.settings')

try:
    django.setup()
except AttributeError:
    print(django.VERSION)

from django.contrib.auth.management.commands import changepassword
from django.core import management

# # Create the super user and sets his password.
management.call_command('createsuperuser', interactive=False, username="admin", email="arclytics@neuraldev.io")
command = changepassword.Command()
command._get_pass = lambda *args: 'DirectorFury'
command.execute("admin")
