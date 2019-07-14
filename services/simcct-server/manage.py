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
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""manage.py: 

This script is to our CLI script tool to manage the application.
"""

import os
import sys
import unittest

from flask.cli import FlaskGroup
import coverage

from sim_api import create_app

COV = coverage.coverage(
    branch=True,
    include=[
        'sim_api/resources/session.py',
        'sim_api/resources/sim_configurations.py',
        'sim_api/schemas.py',
        'sim_api/middleware.py',
    ],
    omit=[
        'sim_api/__init__.py'
        'tests/*',
        'configs/*',
        'logs/*',
    ]
)
COV.start()

app = create_app()
cli = FlaskGroup(create_app=create_app)


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
    result = unittest.TextTestRunner(verbosity=4).run(tests)
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
