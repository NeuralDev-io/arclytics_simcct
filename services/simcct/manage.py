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
import json
import sys
import unittest
from pathlib import Path

import coverage
from flask.cli import FlaskGroup
from pymongo import MongoClient

from sim_app.app import create_app

COV = coverage.coverage(
    branch=True,
    include=[
        'sim_app/schemas.py',
        'sim_app/resources/*',
        'sim_app/alloys/*',
        'sim_app/alloys_service.py',
        'sim_app/middleware.py',
    ],
    omit=[
        'sim_app/__init__.py'
        'tests/*',
        'configs/*',
        'logs/*',
    ]
)
COV.start()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('seed_db')
def seed_alloy_db():
    client = MongoClient(
        host=os.environ.get('MONGO_HOST'),
        port=int(os.environ.get('MONGO_PORT'))
    )
    db = client['arc_dev']
    path = Path(BASE_DIR) / 'seed_alloy_data.json'
    if os.path.isfile(path):
        with open(path) as f:
            json_data = json.load(f)

    from sim_app.schemas import AlloySchema
    data = AlloySchema(many=True).load(json_data['alloys'])
    db.alloys.insert_many(data)
    import pprint
    for alloy in db.alloys.find():
        pprint.pprint(alloy)


@cli.command('flush')
def flush():
    client = MongoClient(
        host=os.environ.get('MONGO_HOST'),
        port=int(os.environ.get('MONGO_PORT'))
    )
    client.drop_database('arc')
    client.drop_database('arc_dev')
    client.drop_database('arc_test')


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
