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


class Method(enum.Enum):
    Li98 = 1
    Kirkaldy83 = 2


class Alloy(enum.Enum):
    Parent = 1
    Weld = 2
    Mix = 3


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
