/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * A wrapper around Tanner Linsley's React Table with custom styles.
 * https://github.com/tannerlinsley/react-table
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import ReactTable from 'react-table'

import './Table.scss'

// TODO: add custom pagination component
const Table = props => (
  <ReactTable
    {...props}
  />
)

export default Table
