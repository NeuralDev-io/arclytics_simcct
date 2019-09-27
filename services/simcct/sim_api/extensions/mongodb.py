# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# mongodb.py
#
# Attributions:
# [1]
# https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.04'
"""mongodb.py: 

This module defines a singleton instance of a PyMongo MongoClient using the 
MongoEngine interface.
"""
from pymongo import MongoClient


class MongoSingleton:
    instance = None

    class __Mongo:
        def __init__(self, obj: MongoClient):
            self.client = obj

        def __str__(self):
            return '__Mongo.MongoClient'

    def __init__(self, obj: MongoClient):
        if not MongoSingleton.instance:
            MongoSingleton.instance = MongoSingleton.__Mongo(obj=obj)
        else:
            MongoSingleton.instance.inst = obj

    def __getattr__(self, item):
        return getattr(self.instance, item)
