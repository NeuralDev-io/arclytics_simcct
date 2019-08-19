import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import withDimension from 'react-dimensions'
import { layout, config } from './utils/chartConfig'

import colours from '../../../styles/_colors_light.scss'
import styles from './CCT.module.scss'

const CCT = ({
  containerHeight,
  containerWidth,
  data,
  userData,
  showUserCurve,
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

    if (showUserCurve) {
      chartData.push({
        x: userData.time,
        y: userData.temp,
        name: 'User cooling curve',
        mode: 'line',
        marker: {
          width: 4,
          color: colours.r500,
          line: { width: 4 },
        },
      })
    }
  }

  if (chartData.length === 0) {
    return <div className={styles.noData}>No data.</div>
  }

  return (
    <Plot
      data={chartData}
      layout={{
        ...layout(containerWidth, containerHeight),
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
  )
}

const linePropTypes = PropTypes.shape({
  temp: PropTypes.arrayOf(PropTypes.number),
  time: PropTypes.arrayOf(PropTypes.number),
})

CCT.propTypes = {
  showUserCurve: PropTypes.bool.isRequired,
  // props given by withDimension()
  containerWidth: PropTypes.number.isRequired,
  containerHeight: PropTypes.number.isRequired,
  // props given by connect()
  data: PropTypes.shape({
    ferrite_nucleation: linePropTypes,
    ferrite_completion: linePropTypes,
    pearlite_nucleation: linePropTypes,
    pearlite_completion: linePropTypes,
    bainite_nucleation: linePropTypes,
    bainite_completion: linePropTypes,
    martensite: linePropTypes,
    // user_cooling_curve: linePropTypes,
  }).isRequired,
}

const mapStateToProps = state => ({
  data: state.sim.results.CCT,
  userData: state.sim.results.user_cooling_curve,
})

export default withDimension({
  className: styles.wrapper,
})(connect(mapStateToProps, {})(CCT))
