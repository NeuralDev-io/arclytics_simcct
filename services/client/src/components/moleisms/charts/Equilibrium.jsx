/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Equilibrium chart.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { InlineSpinner } from '../../elements/spinner'
import { layout, config } from './utils/chartConfig'
import { getEquilibriumValues } from '../../../state/ducks/equi/actions'

import { getColor } from '../../../utils/theming'
import styles from './Equilibrium.module.scss'

class Equilibrium extends React.Component {
  componentDidMount = () => {
    const { data, isInitialised, getEquilibriumValuesConnect } = this.props
    console.log('just mounted')
    if (isInitialised && (data === undefined || data === null || Object.keys(data).length === 0)) {
      console.log('getting data')
      getEquilibriumValuesConnect()
    }
  }

  // If alloys or ae1_temp is updated (because a cached sim was loaded from persisted storage
  // or account), get the plot results with new alloys/ae1_temp.
  componentDidUpdate = (prevProps) => {
    const {
      isInitialised,
      alloys,
      ae1Temp,
      getEquilibriumValuesConnect,
    } = this.props

    // only make API request if an alloy was chosen
    if (isInitialised && (prevProps.alloys !== alloys || prevProps.ae1Temp !== ae1Temp)) {
      console.log('getting data after updated')
      getEquilibriumValuesConnect()
    }
  }

  render() {
    const { data, isLoading, isInitialised } = this.props
    let chartData = []
    if (isInitialised && data !== undefined && data !== null && Object.keys(data).length !== 0) {
      chartData = [
        {
          x: data.ae1.x,
          y: data.ae1.y,
          name: 'Ae1',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--v500'),
            shape: 'spline',
          },
        },
        {
          x: data.ae3.x,
          y: data.ae3.y,
          name: 'Ae3',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--o500'),
            shape: 'spline',
          },
        },
        {
          x: data.t0.x,
          y: data.t0.y,
          name: 'T0',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--r500'),
            shape: 'spline',
          },
        },
        {
          x: data.cf.x,
          y: data.cf.y,
          name: 'Cf',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--g500'),
            shape: 'spline',
          },
        },
        {
          x: data.c_wt.x,
          y: data.c_wt.y,
          name: 'Carbon weight percentage',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--m500'),
            shape: 'spline',
          },
        },
      ]
    }

    if (chartData.length === 0) {
      if (isLoading) {
        return (
          <div className={styles.noData}>
            <InlineSpinner />
          </div>
        )
      }
      if (!isInitialised) {
        return <div className={styles.noData}>Please choose an alloy first.</div>
      }
      return <div className={styles.noData}>No data.</div>
    }

    return (
      <AutoSizer>
        {({ height, width }) => {
          const defaultLayout = { ...layout(height, width) }
          return (
            <Plot
              data={chartData}
              layout={{
                ...defaultLayout,
                xaxis: {
                  ...defaultLayout.xaxis,
                  title: 'C (wt%)',
                  autorange: true,
                  tickvals: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                  ticktext: ['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'],
                },
                yaxis: {
                  ...defaultLayout.yaxis,
                  title: 'Temperature (°C)',
                  autorange: true,
                  rangemode: 'nonnegative',
                },
              }}
              config={config}
            />
          )
        }}
      </AutoSizer>
    )
  }
}

const linePropTypes = PropTypes.shape({
  x: PropTypes.arrayOf(PropTypes.number),
  y: PropTypes.arrayOf(PropTypes.number),
})

Equilibrium.propTypes = {
  // props given by connect()
  data: PropTypes.shape({
    ae1: linePropTypes,
    ae3: linePropTypes,
    t0: linePropTypes,
    cf: linePropTypes,
    c_wt: linePropTypes,
  }),
  isLoading: PropTypes.bool.isRequired,
  isInitialised: PropTypes.bool.isRequired,
  getEquilibriumValuesConnect: PropTypes.func.isRequired,
  alloys: PropTypes.shape({}).isRequired,
  ae1Temp: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string,
  ]).isRequired,
}

Equilibrium.defaultProps = {
  data: undefined,
}

const mapStateToProps = state => ({
  data: state.equi.plot,
  isLoading: state.equi.isLoading,
  isInitialised: state.sim.isInitialised,
  alloys: state.sim.alloys,
  ae1Temp: state.sim.configurations.ae1_temp,
})

const mapDispatchToProps = {
  getEquilibriumValuesConnect: getEquilibriumValues,
}

export default connect(mapStateToProps, mapDispatchToProps)(Equilibrium)
