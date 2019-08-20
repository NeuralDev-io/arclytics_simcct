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

This module defines two types of objects. The ResultsMatrix is a wrapper class
on the `numpy.ndarray` filled with zeros. This class can only ever be 2 columns
and the user must define the number of rows. We need this custom wrapper to 
allow dynamic allocation as elements are added to the array.

The other class defines a ResultsData object where we can store the 
ResultsMatrix internally for the Simulation instance. It also has methods to 
accomplish some simple File IO tasks such as saving to CSV, JSON, or pickle.
"""

import csv
import math
import numpy as np
from typing import Union, Tuple, Optional


class ResultsMatrix(object):
    """
    This is a Rank-2 Array wrapper around a `numpy.ndarray` filled with zeros
    using numpy.zeros(). By default, the shape of the `ndarray` will always of
    the dimensions `rows` x 2 as we only ever need 2 columns in this instance.
    By default, we also always use a `C` like order on the `ndarray` with
    `np.float32` as the data type.

    Usage:
        # This will get you [[0., 0.], [0., 0.]] `numpy.ndarray`
        mat = ResultsMatrix(rows=2)
    """
    def __init__(self, rows: int = 1, dtype: Optional[object] = np.float32):
        """Initialise the internal `numpy.ndarray` object with the shape passed
        in from the rows with a default of 2 columns.

        Args:
            rows: the number of rows in the Rank-2 Array dimension.
            dtype: the data type of the elements in the `numpy.ndarray`.
        """
        self.obj = np.zeros(shape=(rows, 2), dtype=dtype, order='C')
        # add the new attributes to the created instance
        self.shape = self.obj.shape
        self.rows = rows
        self.cols = 2

    def __getitem__(self, index: Union[Tuple[int, int], int]) -> float:
        """Using the `[]` operators, this will get you the element stored at
        the index passed in.

        Usage:
            mat = ResultsMatrix(rows=2)
            mat[0, 0] = 10.0
            print(mat[0, 0])  # will print 10.0

        Args:
            index: the index to access the array element as either a tuple
                   (will get you an element) or an int (will

        Returns:
            The value of the element.
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
            self.shape = (new_rows, 2)
        # If resizing need, or otherwise, set item
        self.obj.__setitem__(key, value)

    def __delitem__(self, key):
        del self.obj[key]

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
        self.obj.resize((n_rows, 2), refcheck=True)

    def trim_zeros(self):
        """
        Trim the zeros from the `numpy.zeros` `ndarray` and return each column
        as a (column1, column2).
        """
        return np.trim_zeros(self.obj[:, 0]), np.trim_zeros(self.obj[:, 1])

    def append(self, row: int, value1: float, value2: float) -> None:
        """Append an element to a row in the internal `numpy.ndarray` using

        Usage:
            mat =  ResultsMatrix(rows=2)
            mat.append(0, 1.0, 2.0)
            # Would result in:
            #  [[1., 2.], [0., 0.]]

        Args:
            row: the row index to use.
            value1: the value for the first column or [row, 0].
            value2: the value for the second column or [row, 1].

        Returns:
            None
        """
        self.obj[row, 0] = value1
        self.obj[row, 1] = value2

    def to_dict(self):
        """
        Return the dictionary representation of this `numpy.ndarray` as a list
        with trimmed zeros and as a dictionary of `time` and `temp` keys.
        """
        return self.__dict__()

    def __dict__(self):
        """Internal __dict__ representation of object."""
        time, temp = self.trim_zeros()
        return {'time': time.tolist(), 'temp': temp.tolist()}

    def __str__(self):
        return f'ResultsMatrix(\n{self.obj.__str__()}\n)'

    def __repr__(self):
        return self.obj.__repr__()


class ResultsData(object):
    """
    This class is used to store TTT and CCT plotting data. There will also be
    some helper instance methods to allow plotting with Plotly or printing to
    stdout.
    """
    def __init__(self):
        self.user_cooling_curve: Union[ResultsMatrix, None] = None

        self.ttt_fcs: Union[ResultsMatrix, None] = None
        self.ttt_fcf: Union[ResultsMatrix, None] = None
        self.ttt_pcs: Union[ResultsMatrix, None] = None
        self.ttt_pcf: Union[ResultsMatrix, None] = None
        self.ttt_bcs: Union[ResultsMatrix, None] = None
        self.ttt_bcf: Union[ResultsMatrix, None] = None
        self.ttt_msf: Union[ResultsMatrix, None] = None

        self.cct_fcs: Union[ResultsMatrix, None] = None
        self.cct_fcf: Union[ResultsMatrix, None] = None
        self.cct_pcs: Union[ResultsMatrix, None] = None
        self.cct_pcf: Union[ResultsMatrix, None] = None
        self.cct_bcs: Union[ResultsMatrix, None] = None
        self.cct_bcf: Union[ResultsMatrix, None] = None
        self.cct_msf: Union[ResultsMatrix, None] = None

    @classmethod
    def from_json(cls):
        pass

    @classmethod
    def from_csv(cls):
        pass

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

    def set_user_cool_plot_data(self, user_cooling_data) -> None:
        self.user_cooling_curve = user_cooling_data

    def get_cct_plot_data(self) -> dict:
        return {
            'ferrite_nucleation': self.cct_fcs.to_dict(),
            'ferrite_completion': self.cct_fcf.to_dict(),
            'pearlite_nucleation': self.cct_pcs.to_dict(),
            'pearlite_completion': self.cct_pcf.to_dict(),
            'bainite_nucleation': self.cct_bcs.to_dict(),
            'bainite_completion': self.cct_bcf.to_dict(),
            'martensite': self.cct_msf.to_dict()
        }

    def get_ttt_plot_data(self) -> dict:
        return {
            'ferrite_nucleation': self.ttt_fcs.to_dict(),
            'ferrite_completion': self.ttt_fcf.to_dict(),
            'pearlite_nucleation': self.ttt_pcs.to_dict(),
            'pearlite_completion': self.ttt_pcf.to_dict(),
            'bainite_nucleation': self.ttt_bcs.to_dict(),
            'bainite_completion': self.ttt_bcf.to_dict(),
            'martensite': self.ttt_msf.to_dict()
        }

    def get_user_cool_plot_data(self) -> dict:
        return self.user_cooling_curve.to_dict()

    def plot_cct(self):
        # plot with plotly
        pass

    def plot_ttt(self):
        # plot with plotly
        pass

    @staticmethod
    def to_json(data: dict):
        pass

    @staticmethod
    def to_string(plot: str = ''):
        if plot.lower() == 'cct':
            # stringify cct
            return 'cct'
        elif plot.lower() == 'ttt':
            # stringify ttt
            return 'ttt'

        return 'Error'

    def to_csv(self, plot: str = '', path: str = '') -> None:
        pass

    @staticmethod
    def to_pickle(plot: str = '', path: str = ''):
        if plot.lower() == 'cct':
            # pickle export cct
            pass
        elif plot.lower() == 'ttt':
            # pickle export ttt
            pass

    def __str__(self):
        # print something else other than data
        pass
