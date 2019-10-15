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
    if (isInitialised && (data === undefined || data === null || Object.keys(data).length === 0)) {
      getEquilibriumValuesConnect()
    }
  }

  render() {
    const { data, isLoading, isInitialised } = this.props
    let chartData = []
    if (isInitialised && data !== undefined && data !== null && Object.keys(data).length !== 0) {
      chartData = [
        {
          x: data.ae3.time,
          y: data.ae3.temp,
          name: 'Ae3',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--o500'),
            shape: 'spline',
          },
        },
        {
          x: data.t0.time,
          y: data.t0.temp,
          name: 'T0',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--r500'),
            shape: 'spline',
          },
        },
        {
          x: data.cf.time,
          y: data.cf.temp,
          name: 'Cf',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--l500'),
            shape: 'spline',
          },
        },
        {
          x: data.ae1.time,
          y: data.ae1.temp,
          name: 'Ae1',
          type: 'scatter',
          mode: 'lines',
          line: {
            color: getColor('--g500'),
            shape: 'spline',
          },
        },
        // {
        //   x: data.bainite_nucleation.time,
        //   y: data.bainite_nucleation.temp,
        //   name: 'C-wt',
        //   type: 'scatter',
        //   mode: 'lines',
        //   line: {
        //     color: getColor('--m500'),
        //     shape: 'spline',
        //   },
        // },
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
                  title: 'Time (s)',
                  type: 'log',
                  autorange: true,
                },
                yaxis: {
                  ...defaultLayout.yaxis,
                  title: 'Temperature (°C)',
                  autorange: true,
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
  temp: PropTypes.arrayOf(PropTypes.number),
  time: PropTypes.arrayOf(PropTypes.number),
})

Equilibrium.propTypes = {
  // props given by connect()
  data: PropTypes.shape({
    ae1: linePropTypes,
    ae3: linePropTypes,
    t0: linePropTypes,
    cf: linePropTypes,
  }),
  isLoading: PropTypes.bool.isRequired,
  isInitialised: PropTypes.bool.isRequired,
  getEquilibriumValuesConnect: PropTypes.func.isRequired,
}

Equilibrium.defaultProps = {
  data: undefined,
}

const mapStateToProps = state => ({
  data: state.equi.plot,
  isLoading: state.equi.isLoading,
  isInitialised: state.sim.isInitialised,
})

const mapDispatchToProps = {
  getEquilibriumValuesConnect: getEquilibriumValues,
}

export default connect(mapStateToProps, mapDispatchToProps)(Equilibrium)
