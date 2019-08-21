import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { layout, config } from './utils/chartConfig'

import colours from '../../../styles/_colors_light.scss'
import styles from './CCT.module.scss'

const CCT = ({
  data,
  userData,
  displayUserCurve,
}) => {
  let chartData = []
  if (data !== undefined) {
    chartData = [
      {
        x: data.ferrite_nucleation.time,
        y: data.ferrite_nucleation.temp,
        name: 'Ferrite nucleation',
        mode: 'line',
        marker: { color: colours.o500 },
      },
      {
        x: data.ferrite_completion.time,
        y: data.ferrite_completion.temp,
        name: 'Ferrite completion',
        mode: 'line',
        marker: { color: colours.l500 },
      },
      {
        x: data.pearlite_nucleation.time,
        y: data.pearlite_nucleation.temp,
        name: 'Pearlite nucleation',
        mode: 'line',
        marker: { color: colours.g500 },
      },
      {
        x: data.pearlite_completion.time,
        y: data.pearlite_completion.temp,
        name: 'Pearlite completion',
        mode: 'line',
        marker: { color: colours.t500 },
      },
      {
        x: data.bainite_nucleation.time,
        y: data.bainite_nucleation.temp,
        name: 'Bainite nucleation',
        mode: 'line',
        marker: { color: colours.b500 },
      },
      {
        x: data.bainite_completion.time,
        y: data.bainite_completion.temp,
        name: 'Bainite completion',
        mode: 'line',
        marker: { color: colours.i500 },
      },
      {
        x: data.martensite.time,
        y: data.martensite.temp,
        name: 'Martensite',
        mode: 'line',
        marker: { color: colours.v500 },
      },
    ]

    if (displayUserCurve) {
      chartData.push({
        x: userData.user_cooling_curve.time,
        y: userData.user_cooling_curve.temp,
        name: 'User cooling curve',
        mode: 'line',
        marker: {
          size: 10,
          color: colours.r500,
          line: { width: 10, color: colours.r500 },
        },
      })
    }
  }

  if (chartData.length === 0) {
    return <div className={styles.noData}>No data.</div>
  }

  return (
    <AutoSizer>
      {({ height, width }) => (
        <Plot
          data={chartData}
          layout={{
            ...layout(height, width),
            xaxis: {
              type: 'log',
              autorange: true,
            },
            yaxis: {
              type: 'normal',
              autorange: true,
            },
          }}
          config={config}
        />
      )}
    </AutoSizer>
  )
}

const linePropTypes = PropTypes.shape({
  temp: PropTypes.arrayOf(PropTypes.number),
  time: PropTypes.arrayOf(PropTypes.number),
})

CCT.propTypes = {
  displayUserCurve: PropTypes.bool.isRequired,
  // props given by connect()
  data: PropTypes.shape({
    ferrite_nucleation: linePropTypes,
    ferrite_completion: linePropTypes,
    pearlite_nucleation: linePropTypes,
    pearlite_completion: linePropTypes,
    bainite_nucleation: linePropTypes,
    bainite_completion: linePropTypes,
    martensite: linePropTypes,
  }).isRequired,
  userData: PropTypes.shape({
    user_cooling_curve: linePropTypes,
    user_phase_fraction_data: PropTypes.array,
    slider_time_field: PropTypes.number,
    slider_temp_field: PropTypes.number,
    slider_max: PropTypes.number,
  }).isRequired,
}

CCT.defaultProps = {
  data: undefined,
  userData: undefined,
}

const mapStateToProps = state => ({
  data: state.sim.results.CCT,
  userData: state.sim.results.USER,
  displayUserCurve: state.sim.displayUserCurve,
})

export default connect(mapStateToProps, {})(CCT)
