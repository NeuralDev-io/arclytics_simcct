# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# setup.py
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
__date__ = '2019.09.14'
"""setup.py: 

{Description}
"""

import setuptools

setuptools.setup(
    name='simulation',
    version='0.2',
    author="Andrew Che",
    author_email="andrew@neuraldev.io",
    description="SimCCT Simulation package.",
    url="",
    packages=['simulation'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['prettytable'],
    zip_safe=False
)
