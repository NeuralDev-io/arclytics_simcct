import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import withDimension from 'react-dimensions'
import { layout, config } from './utils/chartConfig'

import colours from '../../../styles/_colors_light.scss'
import styles from './TTT.module.scss'

const TTT = (props) => {
  const { containerWidth, containerHeight, data } = props // eslint-disable-line
  let chartData = []
  if (data !== undefined) {
    chartData = [
      {
        x: data.ferrite_start.time,
        y: data.ferrite_start.temp,
        name: 'Ferrite start',
        mode: 'line',
        marker: { color: colours.o500 },
      },
      {
        x: data.ferrite_finish.time,
        y: data.ferrite_finish.temp,
        name: 'Ferrite finish',
        mode: 'line',
        marker: { color: colours.l500 },
      },
      {
        x: data.pearlite_start.time,
        y: data.pearlite_start.temp,
        name: 'Pearlite start',
        mode: 'line',
        marker: { color: colours.g500 },
      },
      {
        x: data.pearlite_finish.time,
        y: data.pearlite_finish.temp,
        name: 'Pearlite finish',
        mode: 'line',
        marker: { color: colours.t500 },
      },
      {
        x: data.bainite_start.time,
        y: data.bainite_start.temp,
        name: 'Bainite start',
        mode: 'line',
        marker: { color: colours.b500 },
      },
      {
        x: data.bainite_finish.time,
        y: data.bainite_finish.temp,
        name: 'Bainite finish',
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
          autorange: true
        },
        yaxis: {
          type: 'log',
          autorange: true
        }
      }}
      config={config}
    />
  )
}

TTT.propTypes = {
  // props given by withDimension()
  containerWidth: PropTypes.number.isRequired,
  containerHeight: PropTypes.number.isRequired,
  // props given by connect()
  data: PropTypes.object.isRequired, // eslint-disable-line
  // TODO: will add later
}

const mapStateToProps = state => ({
  data: state.sim.results.TTT,
})

export default withDimension({
  className: styles.wrapper,
})(connect(mapStateToProps, {})(TTT))
