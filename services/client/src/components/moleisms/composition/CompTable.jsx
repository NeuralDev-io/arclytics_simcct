import React, { Component } from 'react'
import PropTypes from 'prop-types'
import withDimension from 'react-dimensions'
import Table from '../../elements/table'
import { SelfControlledTextField } from '../../elements/textfield'

import styles from './CompTable.module.scss'

class CompTable extends Component {
  updateComp = (name, value) => {

  }

  render() {
    const { data, onChange, containerHeight } = this.props
    const {
      alloyOption,
      parent,
      weld,
    } = data

    let tableData = parent.compositions.map(elem => ({
      symbol: elem.symbol,
      parent: elem.weight,
      weld: undefined,
      mix: undefined,
    }))
    if (alloyOption === 'both' || alloyOption === 'mix') {
      weld.compositions.forEach((elem) => {
        const idx = tableData.findIndex(x => x.symbol === elem.symbol)
        if (idx === -1) {
          tableData.push({
            symbol: elem.symbol,
            parent: undefined,
            weld: elem.weight,
            mix: undefined,
          })
        } else {
          tableData[idx] = {
            ...tableData[idx],
            weld: elem.weight,
          }
        }
      })
    }
    if (alloyOption === 'mix') {
      const dialution = parseFloat(data.dialution)
      tableData.forEach((elem, idx) => {
        const parentVal = elem.parent ? parseFloat(elem.parent) : 0
        const weldVal = elem.weld ? parseFloat(elem.weld) : 0
        // calculate mix composition and round to 2 decimals
        const mixVal = Math.round((dialution / 100 * weldVal
          + (100 - dialution) / 100 * parentVal) * 100) / 100
        tableData[idx] = {
          ...elem,
          mix: mixVal,
        }
      })
    }

    // calculate total weights
    let parentTotal = 0
    let weldTotal = 0
    let mixTotal = 0
    tableData.forEach((elem) => {
      if (elem.parent) parentTotal += parseFloat(elem.parent)
      if (elem.weld) weldTotal += parseFloat(elem.weld)
      if (elem.mix) mixTotal += parseFloat(elem.mix)
    })
    parentTotal = Math.round(parentTotal * 100) / 100
    weldTotal = Math.round(weldTotal * 100) / 100
    mixTotal = Math.round(mixTotal * 100) / 100

    const columns = [
      {
        Header: 'Elements',
        accessor: 'symbol',
        // eslint-disable-next-line
        Cell: ({ value }) => (<span className={styles.symbol}>{value}</span>),
        width: 80,
        Footer: 'Total',
      },
      {
        Header: 'Alloy 1',
        accessor: 'parent',
        // eslint-disable-next-line
        Cell: ({ row, value }) => (
          <SelfControlledTextField
            type="text"
            name={`parent_${row.symbol}`} // eslint-disable-line
            onBlur={e => onChange(`parent_${row.symbol}`, e.target.value)} // eslint-disable-line
            defaultValue={value || '0.0'}
            length="stretch"
            isDisabled={value === undefined}
          />
        ),
        Footer: () => <span className={styles.footerText}>{parentTotal}</span>,
      },
      {
        Header: 'Alloy 2',
        accessor: 'weld',
        // eslint-disable-next-line
        Cell: ({ row, value }) => (
          <SelfControlledTextField
            type="text"
            name={`weld_${row.symbol}`} // eslint-disable-line
            onBlur={e => onChange(`weld_${row.symbol}`, e.target.value)} // eslint-disable-line
            defaultValue={value || '0.0'}
            length="stretch"
            isDisabled={value === undefined}
          />
        ),
        Footer: () => <span className={styles.footerText}>{weldTotal}</span>,
      },
      {
        Header: 'Mix',
        accessor: 'mix',
        // eslint-disable-next-line
        Cell: ({ value }) => {
          if (value === undefined) return <span className="text--disabled">0.0</span>
          return <span>{value}</span>
        },
        width: 40,
        Footer: mixTotal,
      },
    ]

    return (
      <Table
        data={tableData}
        columns={columns}
        pageSize={Math.round((containerHeight - 124) / 56)}
        showPageSizeOptions={false}
        showPagination={tableData.length !== 0}
        resizable={false}
        hideDivider
        condensed
      />
    )
  }
}

CompTable.propTypes = {
  // props given by withDimension()
  containerHeight: PropTypes.number.isRequired,
  data: PropTypes.shape({
    alloyOption: PropTypes.string,
    parent: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    weld: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    mix: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    dialution: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  }).isRequired,
  onChange: PropTypes.func.isRequired,
}

export default withDimension({
  className: styles.wrapper,
})(CompTable)
