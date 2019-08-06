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
        x: data['Ferrite-nuc'].time,
        y: data['Ferrite-nuc'].temp,
        name: 'Ferrite nucleation',
        mode: 'line',
        marker: { color: colours.o500 },
      },
      {
        x: data['Ferrite-comp'].time,
        y: data['Ferrite-comp'].temp,
        name: 'Ferrite completion',
        mode: 'line',
        marker: { color: colours.l500 },
      },
      {
        x: data['Pearlite-nuc'].time,
        y: data['Pearlite-nuc'].temp,
        name: 'Pearlite nucleation',
        mode: 'line',
        marker: { color: colours.g500 },
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

TTT.propTypes = {
  // props given by withDimension()
  containerWidth: PropTypes.number.isRequired,
  containerHeight: PropTypes.number.isRequired,
  // props given by connect()
  data: PropTypes.object.isRequired, // eslint-disable-line
  // TODO: will add later
}

const mapStateToProps = state => ({
  data: state.sim.results['TTT Data'],
})

export default withDimension({
  className: styles.wrapper,
})(connect(mapStateToProps, {})(TTT))
