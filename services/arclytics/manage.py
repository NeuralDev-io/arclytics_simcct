#!/opt/conda/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# manage.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '0.1.0'
__status__ = 'development'
__date__ = '2019.07.09'
"""manage.py: 

This script is to our CLI script tool to manage the application.
"""

import os
import sys
import unittest

import coverage
from flask.cli import FlaskGroup

from arc_api import create_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

COV = coverage.coverage(
    branch=True,
    include=[],
    omit=['arc_api/__init__.py']
)
COV.start()

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('flush')
def flush():
    pass


@cli.command('seed_db')
def seed_user_db():
    pass


@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)


@cli.command('test_coverage')
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('\nCoverage Summary:')
        COV.report(show_missing=False)
        COV.html_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
