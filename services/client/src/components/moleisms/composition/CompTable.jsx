import React from 'react'
import PropTypes from 'prop-types'
import Table from '../../elements/table'
import TextField from '../../elements/textfield'

import styles from './CompTable.module.scss'

const CompTable = (props) => {
  const { data = [], onChange } = props
  const columns = [
    {
      Header: 'Elements',
      accessor: 'name',
      width: 100,
    },
    {
      Header: '',
      accessor: 'symbol',
      // eslint-disable-next-line
      Cell: ({ value }) => (<span className={styles.symbol}>{value}</span>),
      width: 40,
    },
    {
      Header: 'Weight (Alloy 1)',
      accessor: 'weight',
      id: ({ row }) => row.name,
      // eslint-disable-next-line
      Cell: ({ row, value }) => (
        <TextField
          type="text"
          name={row.name} // eslint-disable-line
          onChange={val => onChange(row.name, val)} // eslint-disable-line
          value={value}
          length="short"
        />
      ),
    },
  ]

  return (
    <Table
      data={data}
      columns={columns}
      defaultPageSize={7}
      showPageSizeOptions={false}
      showPagination={data.length !== 0}
      resizable={false}
      hideDivider
      condensed
    />
  )
}

CompTable.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    symbol: PropTypes.string,
    weight: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  })),
  onChange: PropTypes.func.isRequired,
}

CompTable.defaultProps = {
  data: [],
}

export default CompTable
