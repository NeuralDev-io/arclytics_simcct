/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Phase fractions component, includes the vertical slider, a phase fraction
 * pie chart and legends for the phase fractions
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import VerticalSlider from '../../elements/slider'
import { InlineSpinner } from '../../elements/spinner'
import { config } from './utils/chartConfig'
import { roundTo } from '../../../utils/math'
import { getColor } from '../../../utils/theming'
import { updateCCTIndex } from '../../../state/ducks/sim/actions'

import styles from './PhaseFractions.module.scss'

class PhaseFractions extends Component {
  componentWillUnmount = () => {
    const { updateCCTIndexConnect } = this.props
    updateCCTIndexConnect(-1)
  }

  handleUpdateIndex = (values) => {
    const { updateCCTIndexConnect } = this.props
    updateCCTIndexConnect(values[0])
  }

  renderCurrentPercent = (data) => {
    const { labels, values } = data
    const chartColors = [
      getColor('--o500'),
      getColor('--g500'),
      getColor('--t500'),
      getColor('--i500'),
      getColor('--m500'),
    ]
    return labels.map((label, index) => {
      const isDisabled = values[index] === 0
      return (
        <div key={label} className={isDisabled ? styles.disabled : undefined}>
          <div className={styles.label}>
            <div style={{ backgroundColor: isDisabled ? getColor('--n300') : chartColors[index] }} />
            <span>{label}</span>
          </div>
          <span>
            {values[index]}
            &nbsp;%
          </span>
        </div>
      )
    })
  }

  render() {
    const {
      data: {
        user_cooling_curve,
        user_phase_fraction_data: {
          austenite, ferrite, pearlite, bainite, martensite,
        },
        slider_max = -1,
      },
      isLoading,
      cctIndex,
    } = this.props

    const hasData = slider_max !== -1
    // if cctIndex has not been updated, current index is set to
    // last index of data array
    const currentIdx = cctIndex === -1 ? slider_max : cctIndex

    const chartData = [{
      labels: ['Austenite', 'Ferrite', 'Pearlite', 'Bainite', 'Martensite'],
      values: (() => {
        // if there is no data return a dummy array
        if (!hasData) return [0, 0, 0, 0, 0]
        // if there is data return values at current index
        return [
          roundTo(austenite[currentIdx], 1),
          roundTo(ferrite[currentIdx], 1),
          roundTo(pearlite[currentIdx], 1),
          roundTo(bainite[currentIdx], 1),
          roundTo(martensite[currentIdx], 1),
        ]
      })(),
      marker: {
        colors: [
          getColor('--o500'),
          getColor('--g500'),
          getColor('--t500'),
          getColor('--i500'),
          getColor('--m500'),
        ],
      },
      type: 'pie',
      hoverinfo: 'label+percent',
      textinfo: 'none',
      sort: false,
      hole: 0.55,
    }]

    return (
      <div className={styles.chart}>
        <div className={styles.controls}>
          <div className={styles.data}>
            <div className={styles.currentPercent}>
              {this.renderCurrentPercent(chartData[0])}
            </div>
            <div className={styles.timeTemp}>
              <div className={!hasData ? styles.disabled : undefined}>
                <span>{!hasData ? 0 : Math.round(user_cooling_curve.time[currentIdx])}</span>
                <span>s</span>
              </div>
              <div className={!hasData ? styles.disabled : undefined}>
                <span>{!hasData ? 0 : Math.round(user_cooling_curve.temp[currentIdx])}</span>
                <span>°C</span>
              </div>
            </div>
          </div>
          <VerticalSlider
            domain={[0, slider_max]}
            values={[currentIdx]}
            step={1}
            isDisabled={!hasData}
            onUpdate={this.handleUpdateIndex}
          />
        </div>
        <div className={styles.pie}>
          {
            !hasData ? <div className={styles.noData}>{isLoading ? <InlineSpinner /> : 'No data.'}</div>
              : (
                <AutoSizer>
                  {({ height, width }) => (
                    <Plot
                      data={chartData}
                      layout={{
                        width,
                        height,
                        margin: {
                          t: 0,
                          r: 0,
                          b: 0,
                          l: 0,
                          pad: 0,
                        },
                        pad: 12,
                        plot_bgcolor: getColor('--n0'),
                        paper_bgcolor: 'transparent',
                        showlegend: false,
                      }}
                      config={{
                        ...config,
                        displayModeBar: false,
                      }}
                    />
                  )}
                </AutoSizer>
              )
          }
        </div>
      </div>
    )
  }
}

const linePropTypes = PropTypes.shape({
  temp: PropTypes.arrayOf(PropTypes.number),
  time: PropTypes.arrayOf(PropTypes.number),
})

PhaseFractions.propTypes = {
  // props given by connect()
  data: PropTypes.shape({
    user_cooling_curve: linePropTypes,
    user_phase_fraction_data: PropTypes.shape({
      austenite: PropTypes.arrayOf(PropTypes.number),
      ferrite: PropTypes.arrayOf(PropTypes.number),
      pearlite: PropTypes.arrayOf(PropTypes.number),
      bainite: PropTypes.arrayOf(PropTypes.number),
      martensite: PropTypes.arrayOf(PropTypes.number),
    }),
    slider_time_field: PropTypes.number,
    slider_temp_field: PropTypes.number,
    slider_max: PropTypes.number,
  }),
  isLoading: PropTypes.bool.isRequired,
  cctIndex: PropTypes.number.isRequired,
  updateCCTIndexConnect: PropTypes.func.isRequired,
}

PhaseFractions.defaultProps = {
  data: undefined,
}

const mapStateToProps = state => ({
  data: state.sim.results.USER,
  isLoading: state.sim.results.isLoading,
  cctIndex: state.sim.results.cctIndex,
})

const mapDispatchToProps = {
  updateCCTIndexConnect: updateCCTIndex,
}

export default connect(mapStateToProps, mapDispatchToProps)(PhaseFractions)
