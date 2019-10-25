/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * TTT chart. This component takes TTT sim data from Redux store
 * and plots them
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

import { getColor } from '../../../utils/theming'
import styles from './Chart.module.scss'

const TTT = ({ data, isLoading, startTemp }) => {
  let chartData = []
  if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
    chartData = [
      {
        x: data.ferrite_nucleation.time,
        y: data.ferrite_nucleation.temp,
        name: 'Ferrite start',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--o500'),
          shape: 'spline',
        },
      },
      {
        x: data.ferrite_completion.time,
        y: data.ferrite_completion.temp,
        name: 'Ferrite finish',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--r500'),
          shape: 'spline',
        },
      },
      {
        x: data.pearlite_nucleation.time,
        y: data.pearlite_nucleation.temp,
        name: 'Pearlite start',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--l500'),
          shape: 'spline',
        },
      },
      {
        x: data.pearlite_completion.time,
        y: data.pearlite_completion.temp,
        name: 'Pearlite finish',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--g500'),
          shape: 'spline',
        },
      },
      {
        x: data.bainite_nucleation.time,
        y: data.bainite_nucleation.temp,
        name: 'Bainite start',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--m500'),
          shape: 'spline',
        },
      },
      {
        x: data.bainite_completion.time,
        y: data.bainite_completion.temp,
        name: 'Bainite finish',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--v500'),
          shape: 'spline',
        },
      },
      {
        x: data.martensite.time,
        y: data.martensite.temp,
        name: 'Martensite',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--br500'),
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
    return <div className={styles.noData}>No data.</div>
  }

  // Setup the max value for the y-axis
  let ymax
  if (startTemp < 1000) {
    ymax = 1000
  } else {
    ymax = (startTemp < 1500) ? 1500 : startTemp + 100
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
                autorange: false,
                // exponentformat: 'power',
                rangemode: 'nonnegative',
                constrain: 'domain',
                range: [-1.6094379124341003, 4.605170185988092],
              },
              yaxis: {
                ...defaultLayout.yaxis,
                title: 'Temperature (°C)',
                range: [0, ymax],
                rangemode: 'tozero',
                autorange: false,
              },
            }}
            config={config}
          />
        )
      }}
    </AutoSizer>
  )
}

const linePropTypes = PropTypes.shape({
  temp: PropTypes.arrayOf(PropTypes.number),
  time: PropTypes.arrayOf(PropTypes.number),
})

TTT.propTypes = {
  // props given by connect()
  startTemp: PropTypes.number.isRequired,
  data: PropTypes.shape({
    ferrite_nucleation: linePropTypes,
    ferrite_completion: linePropTypes,
    pearlite_nucleation: linePropTypes,
    pearlite_completion: linePropTypes,
    bainite_nucleation: linePropTypes,
    bainite_completion: linePropTypes,
    martensite: linePropTypes,
  }),
  isLoading: PropTypes.bool.isRequired,
}

TTT.defaultProps = {
  data: undefined,
}

const mapStateToProps = state => ({
  data: state.sim.results.TTT,
  startTemp: state.sim.configurations.start_temp,
  isLoading: state.sim.results.isLoading,
})

export default connect(mapStateToProps, {})(TTT)
