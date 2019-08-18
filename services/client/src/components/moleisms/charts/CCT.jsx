import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import withDimension from 'react-dimensions'
import { layout, config } from './utils/chartConfig'

import colours from '../../../styles/_colors_light.scss'
import styles from './CCT.module.scss'

const CCT = (props) => {
  const { containerWidth, containerHeight, data } = props // eslint-disable-line
  let chartData = []
  if (data !== undefined) {
    chartData = [
      {
        x: data.ferrite_nucleation.time,
        y: data.ferrite_nucleation.temp,
        name: 'Ferrite nucleation',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.o500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
      {
        x: data.ferrite_completion.time,
        y: data.ferrite_completion.temp,
        name: 'Ferrite completion',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.l500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
      {
        x: data.pearlite_nucleation.time,
        y: data.pearlite_nucleation.temp,
        name: 'Pearlite nucleation',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.g500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
      {
        x: data.pearlite_completion.time,
        y: data.pearlite_completion.temp,
        name: 'Pearlite completion',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.t500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
      {
        x: data.bainite_nucleation.time,
        y: data.bainite_nucleation.temp,
        name: 'Bainite nucleation',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.b500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
      {
        x: data.bainite_completion.time,
        y: data.bainite_completion.temp,
        name: 'Bainite completion',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.i500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
      {
        x: data.martensite.time,
        y: data.martensite.temp,
        name: 'Martensite',
        mode: 'lines+markers',
        type: 'scattergl',
        marker: {
          color: colours.v500,
          width: 1,
          line: { width: 1, color: 'rgb(0, 0, 0' },
        },
      },
    ]
  }

  if (chartData.length === 0) {
    return <div className={styles.noData}>No data.</div>
  }

  return (
    <Plot
      data={chartData}
      layout={layout(containerWidth, containerHeight)}
      config={config}
    />
  )
}

CCT.propTypes = {
  // props given by withDimension()
  containerWidth: PropTypes.number.isRequired,
  containerHeight: PropTypes.number.isRequired,
  // props given by connect()
  data: PropTypes.object.isRequired, // eslint-disable-line
  // TODO: will add later
}

const mapStateToProps = state => ({
  data: state.sim.results.CCT,
})

export default withDimension({
  className: styles.wrapper,
})(connect(mapStateToProps, {})(CCT))
