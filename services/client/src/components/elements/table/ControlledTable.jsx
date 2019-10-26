/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * A wrapper around Tanner Linsley's React Table with custom styles.
 * https://github.com/tannerlinsley/react-table
 *
 * @version 1.0.0
 * @author Andrew Che
 *
*/
/* eslint-disable react/jsx-props-no-spreading */
import React from 'react'
import PropTypes from 'prop-types'
import ReactTable from 'react-table'
import ServerSidePagination from './ServerSidePagination'

import './Table.scss'

// Custom no-data component. This component won't display if table is
// loading data.
const CustomNoDataComponent = ({ loading }) => (
  loading
    ? (
      <div className="rt-noData">
        Loading...
      </div>
    )
    : (
      <div className="rt-noData">
        No results.
      </div>
    )
)

CustomNoDataComponent.propTypes = {
  loading: PropTypes.bool.isRequired,
}

// Table component
const ControlledTable = (props) => {
  const {
    hideDivider = false,
    condensed = false,
    className = '',
    loading = false,
    fetchData,
    pages,
    defaultPageSize,
    ...otherProps
  } = props
  return (
    <ReactTable
      manual
      onFetchData={fetchData}
      PaginationComponent={ServerSidePagination}
      loading={loading}
      getNoDataProps={noDataProps => ({ loading: noDataProps.loading })}
      NoDataComponent={CustomNoDataComponent}
      defaultPageSize={defaultPageSize}
      pages={pages}
      className={`${hideDivider ? 'rt-hide-divider' : ''} ${condensed ? 'condensed' : ''} ${className}`}
      {...otherProps}
    />
  )
}

ControlledTable.propTypes = {
  fetchData: PropTypes.func.isRequired,
  pages: PropTypes.number.isRequired,
  defaultPageSize: PropTypes.number,
  hideDivider: PropTypes.bool,
  condensed: PropTypes.bool,
  className: PropTypes.string,
  loading: PropTypes.bool,
}

ControlledTable.defaultProps = {
  defaultPageSize: 10,
  hideDivider: false,
  condensed: false,
  className: '',
  loading: false,
}

export default ControlledTable
