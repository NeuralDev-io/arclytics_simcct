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
import PropTypes from 'prop-types'
import ReactTable from 'react-table'
import Pagination from './Pagination'

import './Table.scss'

const Table = (props) => {
  const {
    hideDivider = false,
    condensed = false,
    ...otherProps
  } = props
  return (
    <ReactTable
      {...otherProps}
      className={`${hideDivider ? 'rt-hide-divider' : ''} ${condensed ? 'condensed' : ''}`}
      PaginationComponent={Pagination}
    />
  )
}

Table.propTypes = {
  hideDivider: PropTypes.bool,
  condensed: PropTypes.bool,
}

Table.defaultProps = {
  hideDivider: false,
  condensed: false,
}

export default Table
