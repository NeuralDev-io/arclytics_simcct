import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { layout, config } from './utils/chartConfig'

import { getColor } from '../../../utils/theming'
import styles from './CCT.module.scss'

const CCT = ({
  data,
  userData,
  displayUserCurve,
  cctIndex,
}) => {
  let chartData = []
  if (data !== undefined) {
    chartData = [
      {
        x: data.ferrite_nucleation.time,
        y: data.ferrite_nucleation.temp,
        name: 'Ferrite start',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--o500') },
      },
      {
        x: data.ferrite_completion.time,
        y: data.ferrite_completion.temp,
        name: 'Ferrite finish',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--r500') },
      },
      {
        x: data.pearlite_nucleation.time,
        y: data.pearlite_nucleation.temp,
        name: 'Pearlite start',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--l500') },
      },
      {
        x: data.pearlite_completion.time,
        y: data.pearlite_completion.temp,
        name: 'Pearlite finish',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--g500') },
      },
      {
        x: data.bainite_nucleation.time,
        y: data.bainite_nucleation.temp,
        name: 'Bainite start',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--m500') },
      },
      {
        x: data.bainite_completion.time,
        y: data.bainite_completion.temp,
        name: 'Bainite finish',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--v500') },
      },
      {
        x: data.martensite.time,
        y: data.martensite.temp,
        name: 'Martensite',
        type: 'scatter',
        mode: 'lines',
        line: { color: getColor('--br500') },
      },
      displayUserCurve && {
        x: userData.user_cooling_curve.time,
        y: userData.user_cooling_curve.temp,
        name: 'User cooling curve',
        type: 'scatter',
        mode: 'lines',
        line: {
          color: getColor('--t500'),
          width: 3,
        },
      },
      displayUserCurve && {
        x: cctIndex !== -1
          ? [userData.user_cooling_curve.time[cctIndex]]
          : [userData.user_cooling_curve.time[userData.slider_max]],
        y: cctIndex !== -1
          ? [userData.user_cooling_curve.temp[cctIndex]]
          : [userData.user_cooling_curve.temp[userData.slider_max]],
        name: 'CCT',
        mode: 'markers',
        type: 'scatter',
        marker: {
          color: getColor('--g500'),
          width: 50,
        },
      },
    ]
  }

  if (chartData.length === 0) {
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
  }),
  userData: PropTypes.shape({
    user_cooling_curve: linePropTypes,
    user_phase_fraction_data: PropTypes.shape({}),
    slider_time_field: PropTypes.number,
    slider_temp_field: PropTypes.number,
    slider_max: PropTypes.number,
  }),
  cctIndex: PropTypes.number.isRequired,
}

CCT.defaultProps = {
  data: undefined,
  userData: undefined,
}

const mapStateToProps = state => ({
  data: state.sim.results.CCT,
  userData: state.sim.results.USER,
  cctIndex: state.sim.results.cctIndex,
  displayUserCurve: state.sim.displayUserCurve,
})

export default connect(mapStateToProps, {})(CCT)
