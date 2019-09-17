# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# setup_logger.py
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
__date__ = '2019.09.15'
"""setup_logger.py: 

Setup tools file for Logger package.
"""

import setuptools

setuptools.setup(
    name='logger',
    version='1.0',
    author="Andrew Che",
    author_email="andrew@neuraldev.io",
    description="Application Logger package.",
    packages=['logger'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pprint'],
    zip_safe=False
)
