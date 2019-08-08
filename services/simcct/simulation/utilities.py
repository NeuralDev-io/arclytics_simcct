# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.25'
__package__ = 'simulation'
"""utilities.py: 

Some utilities that are used by SimCCT routines. 
"""

import enum
import numpy as np
from typing import Tuple


class Method(enum.Enum):
    Li98 = 1
    Kirkaldy83 = 2


class Alloy(enum.Enum):
    parent = 1
    weld = 2
    mix = 3


class ElementSymbolInvalid(Exception):
    """Raises an Exception if the Element does not conform to a valid symbol
    as used in the Periodic Table of Elements.
    """
    default_err = (
        'ValidationError (Element) (Field does not match a valid '
        'element symbol in the Periodic Table: ["symbol"])'
    )

    def __init__(self, message=default_err):
        super(ElementSymbolInvalid, self).__init__(message)


class ElementInvalid(Exception):
    """Raises an Exception if the Element is invalid in any way."""
    prefix = 'ValidationError (Element)'

    def __init__(self, message=''):
        super(ElementInvalid, self).__init__(f'{self.prefix} ({message})')


def linear_fit(x_point: float, x1: float, y1: float, x2: float, y2: float):
    """
    Routine to determine the linear fit between two points for a given ratio.
    """
    # calculate gradient
    gradient = (y2 - y1) / (x2 - x1)
    return gradient * (x_point - x1) + y1


def sort_ccr(ccr_mat: np.ndarray) -> np.array:
    """Flattens and sorts the critical cooling rate matrix."""
    return np.sort(ccr_mat.ravel())


def validate_comp_elements(alloy_comp: list) -> Tuple[bool, list]:
    """We validate the alloy has all the elements that will be needed by the
    simulation algorithms using a hashed dictionary as it is much faster.

    Args:
        alloy_comp: a list of Alloy composition objects (i.e.
                    {"symbol": "C", "weight": 1.0})

    Returns:
        A tuple response whether the validation succeeded and the missing
        elements if it did not.
    """
    valid_elements = {
        'C': False,
        'Mn': False,
        'Ni': False,
        'Cr': False,
        'Mo': False,
        'Si': False,
        'Co': False,
        'W': False,
        'As': False,
        'Fe': False
    }

    for el in alloy_comp:
        if el['symbol'] in valid_elements.keys():
            valid_elements[el['symbol']] = True

    # all() returns True if all values in the dict are True
    # If it does not pass, we build up a message and respond.
    if not all(el is True for el in valid_elements.values()):
        # We build up a list of missing elements for the response.
        missing_elem = []
        for k, v in valid_elements.items():
            if not v:
                missing_elem.append(k)
        # The validation has failed so we return False and the missing elements
        return False, missing_elem
    # The validation has succeeded
    return True, []
