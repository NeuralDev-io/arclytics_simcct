# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# dynamic_ndarray.py
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
__package__ = 'simulation'
"""dynamic_ndarray.py: 

This module defines two types of objects. The DynamicNdarray is a wrapper class
on the `numpy.ndarray` filled with zeros. This class can only ever be 2 columns
and the user must define the number of rows. We need this custom wrapper to 
allow dynamic allocation as elements are added to the array.
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
            self.obj = np.zeros(shape=(shape, ), dtype=dtype, order='C')
            self.rows = 0
            self.cols = shape
        # add the new attributes to the created instance
        self.shape = self.obj.shape

    def __getitem__(self, index: Union[Tuple[int, int], int]
                    ) -> Union[float, np.ndarray]:
        """Using the `[]` operators, this will get you the element stored at
        the index passed in.

        Usage:
            mat = DynamicNdarray(rows=2)
            mat[0, 0] = 10.0
            print(mat[0, 0])  # will print 10.0

        Args:
            index: the index to access the array element as either a tuple
                   (will get you an element) or an int.

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
        idx = key[0] if isinstance(key, tuple) else key

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
