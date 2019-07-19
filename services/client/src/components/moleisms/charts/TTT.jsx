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
  data: state.sim['TTT Data'],
})

export default withDimension({
  className: styles.wrapper,
})(connect(mapStateToProps, {})(TTT))
