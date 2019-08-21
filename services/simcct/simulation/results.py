# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# results.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.9.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.01'
"""results.py: 

This module defines two types of objects. The DynamicNdarray is a wrapper class
on the `numpy.ndarray` filled with zeros. This class can only ever be 2 columns
and the user must define the number of rows. We need this custom wrapper to 
allow dynamic allocation as elements are added to the array.

The other class defines a ResultsData object where we can store the 
DynamicNdarray internally for the Simulation instance. It also has methods to 
accomplish some simple File IO tasks such as saving to CSV, JSON, or pickle.
"""

import math
import numpy as np
from typing import Union, Tuple, Optional


class DynamicNdarray(object):
    """
    This is a Rank-2 Array wrapper around a `numpy.ndarray` filled with zeros
    using numpy.zeros(). By default, the shape of the `ndarray` will always of
    the dimensions `rows` x 2 as we only ever need 2 columns in this instance.
    By default, we also always use a `C` like order on the `ndarray` with
    `np.float32` as the data type.

    Usage:
        # This will get you [[0., 0.], [0., 0.]] `numpy.ndarray`
        mat = DynamicNdarray(rows=2)
    """
    def __init__(
            self,
            shape: Union[Tuple[int, int], int],
            dtype: Optional[object] = np.float32
    ):
        """Initialise the internal `numpy.ndarray` object with the shape passed
        in from the rows with a default of 2 columns.

        Args:
            shape: the shape as a tuple or row in the Rank-2 or Rank 1
                   Array dimension.
            dtype: the data type of the elements in the `numpy.ndarray`.
        """
        if isinstance(shape, tuple):
            self.obj = np.zeros(
                shape=(shape[0], shape[1]), dtype=dtype, order='C'
            )
            self.rows = shape[0]
            self.cols = shape[1]
        else:
            self.obj = np.zeros(shape=(shape,), dtype=dtype, order='C')
            self.rows = 0
            self.cols = shape
        # add the new attributes to the created instance
        self.shape = self.obj.shape

    def __getitem__(
            self, index: Union[Tuple[int, int], int]
    ) -> Union[float, np.ndarray]:
        """Using the `[]` operators, this will get you the element stored at
        the index passed in.

        Usage:
            mat = DynamicNdarray(rows=2)
            mat[0, 0] = 10.0
            print(mat[0, 0])  # will print 10.0

        Args:
            index: the index to access the array element as either a tuple
                   (will get you an element) or an int (will

        Returns:
            The value of the element or a `numpy.ndarray` as a copy if
            using slicing
        """
        return self.obj.__getitem__(index)

    def __setitem__(self, key: Union[int, Tuple[int, int]], value) -> None:
        """

        Args:
            key: the key index to store the item as either a tuple (store by
                 m, n position) or int (store the value in every column of the
                 row)
            value: the value to store which must be of the same type as a float

        Returns:
            None
        """
        # Key can be a tuple or an int (fill row)
        if isinstance(key, tuple):
            idx = key[0]
        else:
            idx = key

        # If the key passed is a tuple, meaning indexing by (rows, cols),
        # we check if the rows is more than 75% of the number of rows we
        # currently have. If so, we double our number of rows by 2.
        if idx >= math.floor(self.rows * 0.75):
            new_rows = self.rows * 2
            # Sometimes row index can still be larger so we just double that
            if idx > new_rows:
                new_rows = idx * 2

            self.resize(new_rows)
            self.rows = new_rows
            self.shape = self.obj.shape
        # If resizing need, or otherwise, set item
        self.obj.__setitem__(key, value)

    def __delitem__(self, key):
        del self.obj[key]

    def tolist(self):
        return self.obj.tolist()

    def resize(self, n_rows: int) -> None:
        """Resize the `numpy.ndarray` so that it has n_rows of additional
        rows in the array.

        Args:
            n_rows: an integer of the new rows. Must be larged than self.rows.

        Returns:
            None
        """
        if n_rows < self.rows:
            raise Exception(f'New row size must be bigger than {self.rows}.')
        self.obj.resize((n_rows, self.cols), refcheck=True)
        self.shape = self.obj.shape

    def __str__(self):
        return f'DynamicNdarray(\n{self.obj.__str__()}\n)'

    def __repr__(self):
        return self.obj.__repr__()


def to_plot_dict(array: DynamicNdarray) -> dict:
    assert array.shape[1] == 2, 'Plot Dictionary Array shape must be (n, 2).'
    return {
        'time': array[:, 0].tolist(),
        'temp': array[:, 1].tolist()
    }


class ResultsData(object):
    """
    This class is used to store TTT and CCT plotting data. There will also be
    some helper instance methods to allow plotting with Plotly or printing to
    stdout.
    """
    def __init__(self):
        self.user_cooling_curve: Union[DynamicNdarray, None] = None
        self.user_phase_fraction_data: Union[DynamicNdarray, None] = None
        self.slider_time_field: float = 0.0
        self.slider_temp_field: float = 0.0

        self.ttt_fcs: Union[DynamicNdarray, None] = None
        self.ttt_fcf: Union[DynamicNdarray, None] = None
        self.ttt_pcs: Union[DynamicNdarray, None] = None
        self.ttt_pcf: Union[DynamicNdarray, None] = None
        self.ttt_bcs: Union[DynamicNdarray, None] = None
        self.ttt_bcf: Union[DynamicNdarray, None] = None
        self.ttt_msf: Union[DynamicNdarray, None] = None

        self.cct_fcs: Union[DynamicNdarray, None] = None
        self.cct_fcf: Union[DynamicNdarray, None] = None
        self.cct_pcs: Union[DynamicNdarray, None] = None
        self.cct_pcf: Union[DynamicNdarray, None] = None
        self.cct_bcs: Union[DynamicNdarray, None] = None
        self.cct_bcf: Union[DynamicNdarray, None] = None
        self.cct_msf: Union[DynamicNdarray, None] = None

    def set_cct_plot_data(
        self, ferrite_nucleation, ferrite_completion, pearlite_nucleation,
        pearlite_completion, bainite_nucleation, bainite_completion, martensite
    ) -> None:
        self.cct_fcs = ferrite_nucleation
        self.cct_fcf = ferrite_completion
        self.cct_pcs = pearlite_nucleation
        self.cct_pcf = pearlite_completion
        self.cct_bcs = bainite_nucleation
        self.cct_bcf = bainite_completion
        self.cct_msf = martensite

    def set_ttt_plot_data(
        self, ferrite_nucleation, ferrite_completion, pearlite_nucleation,
        pearlite_completion, bainite_nucleation, bainite_completion, martensite
    ) -> None:
        self.ttt_fcs = ferrite_nucleation
        self.ttt_fcf = ferrite_completion
        self.ttt_pcs = pearlite_nucleation
        self.ttt_pcf = pearlite_completion
        self.ttt_bcs = bainite_nucleation
        self.ttt_bcf = bainite_completion
        self.ttt_msf = martensite

    def set_user_cool_plot_data(
            self, user_cooling_curve, user_phase_fraction_data,
            slider_time_field, slider_temp_field
    ) -> None:
        self.user_cooling_curve = user_cooling_curve
        self.user_phase_fraction_data = user_phase_fraction_data
        self.slider_time_field = slider_time_field
        self.slider_temp_field = slider_temp_field

    def get_cct_plot_data(self) -> dict:
        return {
            'ferrite_nucleation': to_plot_dict(self.cct_fcs),
            'ferrite_completion': to_plot_dict(self.cct_fcf),
            'pearlite_nucleation': to_plot_dict(self.cct_pcs),
            'pearlite_completion': to_plot_dict(self.cct_pcf),
            'bainite_nucleation': to_plot_dict(self.cct_bcs),
            'bainite_completion': to_plot_dict(self.cct_bcf),
            'martensite': to_plot_dict(self.cct_msf)
        }

    def get_ttt_plot_data(self) -> dict:
        return {
            'ferrite_nucleation': to_plot_dict(self.ttt_fcs),
            'ferrite_completion': to_plot_dict(self.ttt_fcf),
            'pearlite_nucleation': to_plot_dict(self.ttt_pcs),
            'pearlite_completion': to_plot_dict(self.ttt_pcf),
            'bainite_nucleation': to_plot_dict(self.ttt_bcs),
            'bainite_completion': to_plot_dict(self.ttt_bcf),
            'martensite': to_plot_dict(self.ttt_msf)
        }

    def get_user_cool_plot_data(self) -> dict:
        return {
            'user_cooling_curve': to_plot_dict(self.user_cooling_curve),
            'user_phase_fraction_data': self.user_phase_fraction_data.tolist(),
            'slider_time_field': self.slider_time_field,
            'slider_temp_field': self.slider_temp_field,
        }
