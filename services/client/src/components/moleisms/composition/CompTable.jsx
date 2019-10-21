/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Composition table, displaying the composition of the alloy chosen
 * in the CompForm component.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import AutoSizer from 'react-virtualized-auto-sizer'
import Table from '../../elements/table'
import { SelfControlledTextField } from '../../elements/textfield'
import { validate } from '../../../utils/validator'
import { constraints } from './utils/constraints'
import { updateComp } from '../../../state/ducks/sim/actions'

import styles from './CompTable.module.scss'

// Some UI elements for alloy 2 and mix composition were commented out
// because the client no longer wants this feature
class CompTable extends Component {
  handleChangeComp = (type, symbol, value) => {
    const { data, updateCompConnect } = this.props
    const alloy = { ...data[type] }
    const idx = alloy.compositions.findIndex(elem => elem.symbol === symbol)
    const newComp = alloy.compositions
    if (idx !== -1) {
      newComp[idx] = {
        ...newComp[idx],
        weight: value,
      }
    }

    let err
    if (symbol === 'C') {
      err = validate(value, constraints.carbon)
    } else {
      err = validate(value, constraints.weight)
    }
    const error = { ...data.parentError }
    if (err !== undefined) {
      error[symbol] = err
    } else {
      delete error[symbol]
    }

    updateCompConnect(data.alloyOption, type, {
      ...alloy,
      compositions: newComp,
    }, error)
  }

  render() {
    const { data } = this.props
    const {
      parentError,
      // alloyOption,
      parent,
      // weld,
    } = data

    const tableData = parent.compositions.map(elem => ({
      symbol: elem.symbol,
      parent: elem.weight,
      weld: undefined,
      mix: undefined,
    }))
    // if (alloyOption === 'mix') {
    //   weld.compositions.forEach((elem) => {
    //     const idx = tableData.findIndex(x => x.symbol === elem.symbol)
    //     if (idx === -1) {
    //       tableData.push({
    //         symbol: elem.symbol,
    //         parent: undefined,
    //         weld: elem.weight,
    //         mix: undefined,
    //       })
    //     } else {
    //       tableData[idx] = {
    //         ...tableData[idx],
    //         weld: elem.weight,
    //       }
    //     }
    //   })
    // }
    // if (alloyOption === 'mix') {
    //   const dilution = parseFloat(data.dilution)
    //   tableData.forEach((elem, idx) => {
    //     const parentVal = elem.parent ? parseFloat(elem.parent) : 0
    //     const weldVal = elem.weld ? parseFloat(elem.weld) : 0
    //     // calculate mix composition and round to 2 decimals
    //     const mixVal = Math.round((dilution / 100 * weldVal
    //       + (100 - dilution) / 100 * parentVal) * 100) / 100
    //     tableData[idx] = {
    //       ...elem,
    //       mix: mixVal,
    //     }
    //   })
    // }

    // calculate total weights
    let parentTotal = 0
    // let weldTotal = 0
    // let mixTotal = 0
    tableData.forEach((elem) => {
      if (elem.parent) parentTotal += parseFloat(elem.parent)
      // if (elem.weld) weldTotal += parseFloat(elem.weld)
      // if (elem.mix) mixTotal += parseFloat(elem.mix)
    })
    parentTotal = Math.round(parentTotal * 100) / 100
    // weldTotal = Math.round(weldTotal * 100) / 100
    // mixTotal = Math.round(mixTotal * 100) / 100

    const columns = [
      {
        Header: 'Elements',
        accessor: 'symbol',
        Cell: ({ value }) => (<span className={styles.symbol}>{value}</span>),
        width: 80,
        ...(() => {
          if (tableData.length !== 0) return { Footer: 'Total' }
          return {}
        })(),
      },
      {
        Header: 'Weight',
        accessor: 'parent',
        Cell: ({ row, value }) => (
          <SelfControlledTextField
            type="text"
            key={row.symbol}
            name={`parent_${row.symbol}`}
            onBlur={e => this.handleChangeComp('parent', row.symbol, e.target.value)}
            defaultValue={value || '0.0'}
            length="stretch"
            isDisabled={value === undefined}
            error={parentError[row.symbol]}
            errorTooltipPosition="left"
          />
        ),
        ...(() => {
          if (tableData.length !== 0) {
            return { Footer: () => <span className={styles.footerText}>{parentTotal}</span> }
          }
          return {}
        })(),
      },
      // {
      //   Header: 'Alloy 2',
      //   accessor: 'weld',
      //   Cell: ({ row, value }) => (
      //     <SelfControlledTextField
      //       type="text"
      //       key={row.symbol}
      //       name={`weld_${row.symbol}`}
      //       onBlur={e => this.handleChangeComp('weld', row.symbol, e.target.value)}
      //       defaultValue={value || '0.0'}
      //       length="stretch"
      //       isDisabled={value === undefined}
      //     />
      //   ),
      //   Footer: () => tableData.length !== 0
      //     && <span className={styles.footerText}>{weldTotal}</span>,
      // },
      // {
      //   Header: 'Mix',
      //   accessor: 'mix',
      //   Cell: ({ value }) => {
      //     if (value === undefined) return <span className="text--disabled">0.0</span>
      //     return <span>{value}</span>
      //   },
      //   width: 40,
      //   Footer: () => tableData.length !== 0
      //     && <span className={styles.footerTextMix}>{mixTotal}</span>,
      // },
    ]

    return (
      <AutoSizer disableWidth>
        {({ height }) => {
          const pageSize = tableData.length !== 0 ? Math.floor((height - 148) / 52) : 0
          return (
            <div className={styles.tableContainer}>
              <Table
                data={tableData}
                columns={columns}
                pageSize={pageSize}
                // The `key` props is added here to force ReactTable to re-render
                // every time height and pageSize is changed
                key={pageSize}
                showPageSizeOptions={false}
                showPagination={tableData.length !== 0}
                resizable={false}
                hideDivider
                condensed
                loading={data.isLoading}
                getTdProps={() => ({ style: { overflow: 'visible' } })}
              />
            </div>
          )
        }}
      </AutoSizer>
    )
  }
}

CompTable.propTypes = {
  data: PropTypes.shape({
    isLoading: PropTypes.bool.isRequired,
    alloyOption: PropTypes.string,
    parentError: PropTypes.shape({}).isRequired,
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
    mix: PropTypes.arrayOf(PropTypes.shape({
      symbol: PropTypes.string,
      weight: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    })),
    dilution: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  }).isRequired,
  updateCompConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  data: state.sim.alloys,
})

const mapDispatchToProps = {
  updateCompConnect: updateComp,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompTable)
