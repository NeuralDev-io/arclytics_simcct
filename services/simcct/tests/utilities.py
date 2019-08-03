# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.31'
"""utilities.py: 

{Description}
"""

from simulation.periodic import PeriodicTable


def convert_json_to_comp(comp_list):
    test_comp = {}
    for el in comp_list:
        try:
            idx = PeriodicTable[el['symbol']].value.atomic_num
        except NotImplementedError as e:
            raise NotImplementedError('Symbol not found error.')
        test_comp[str(idx)] = el
    return test_comp
