# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# abstract_adapter.py.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'

__status__ = 'production'
__date__ = '2019.07.15'
"""abstract_adapter.py.py: 

This module defines an abstract adapter that connects a client to the Alloys
Service such as PyMongo connector client. 
"""


class AlloyAbstract(object):
    """This is an abstract class to be used as an adapter for Alloy Models."""
    def __init__(self, adapter=None):
        self.client = adapter()

    def find_all(self):
        return self.client.find_all()

    def find(self, param):
        return self.client.find(param)

    def create(self, instance):
        return self.client.create(instance)

    def create_many(self, instance_list):
        return self.client.create_many(instance_list)

    def update(self, param, instance):
        return self.client.update(param, instance)

    def delete(self, param):
        return self.client.delete(param)
