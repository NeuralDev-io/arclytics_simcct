# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# abstract_adapter.py.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.15'
"""abstract_adapter.py.py: 

{Description}
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

    def update(self, param, instance):
        return self.client.update(param, instance)

    def delete(self, param):
        return self.client.delete(param)
