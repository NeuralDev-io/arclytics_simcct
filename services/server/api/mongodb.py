# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# mongodb.py
# 
# Attributions: 
# [1] https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.04'
"""mongodb.py: 

This module defines a singleton instance of a PyMongo MongoClient using the MongoEngine interface.
"""
from pymongo import MongoClient


class MongoSingleton(object):
    instance = None

    class __Mongo:
        def __init__(self, obj: MongoClient):
            self.client = obj

        def __str__(self):
            pass

    def __init__(self, obj: MongoClient):
        if not MongoSingleton.instance:
            MongoSingleton.instance = MongoSingleton.__Mongo(obj=obj)
        else:
            MongoSingleton.instance.inst = obj

    def __getattr__(self, item):
        return getattr(self.instance, item)
