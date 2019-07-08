#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# manage.py
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
__date__ = '2019.06.04'
"""manage.py: 

This script is to our CLI script tool to manage the application.
"""

import os
import json
import sys
import unittest
from pathlib import Path

from flask.cli import FlaskGroup
from prettytable import PrettyTable
import coverage

from api import create_app, get_flask_mongo
from api.models import User

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
