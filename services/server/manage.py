# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# manage.py
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
__status__ = 'development'
__date__ = '2019.06.04'
"""manage.py: 

This script is to our CLI script tool to manage the application.
"""

from flask.cli import FlaskGroup

from api import app, User


cli = FlaskGroup(app)


# TODO: Command to recreate database
@cli.command('recreate_db')
def recreate_db():
    test = User(
        email='andrew@neuraldev.io',
        first_name='Andrew',
        last_name='Che',
        username='codeninja55',
        user_type='2'
    ).save()


if __name__ == '__main__':
    cli()
