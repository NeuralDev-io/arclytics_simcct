# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# setup.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
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
    install_requires=['numpy'],
    zip_safe=False
)
