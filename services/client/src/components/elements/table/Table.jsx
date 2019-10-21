/**
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

// Custom no-data component. This component won't display if table is
// loading data.
const CustomNoDataComponent = ({ loading }) => (
  loading
    ? null
    : (
      <div className="rt-noData">
        No data
      </div>
    )
)

CustomNoDataComponent.propTypes = {
  loading: PropTypes.bool.isRequired,
}

// Table component
const Table = (props) => {
  const {
    hideDivider = false,
    condensed = false,
    className = '',
    loading = false,
    ...otherProps
  } = props
  return (
    <ReactTable
      {...otherProps}
      className={`${hideDivider ? 'rt-hide-divider' : ''} ${condensed ? 'condensed' : ''} ${className}`}
      PaginationComponent={Pagination}
      loading={loading}
      getNoDataProps={noDataProps => ({ loading: noDataProps.loading })}
      NoDataComponent={CustomNoDataComponent}
    />
  )
}

Table.propTypes = {
  hideDivider: PropTypes.bool,
  condensed: PropTypes.bool,
  className: PropTypes.string,
  loading: PropTypes.bool,
}

Table.defaultProps = {
  hideDivider: false,
  condensed: false,
  className: '',
  loading: false,
}

export default Table
