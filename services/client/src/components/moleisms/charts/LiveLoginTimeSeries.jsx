/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * This component is a `react-plotly` component wrapper that will be used
 * to poll for live login data and display a time series scatter plot of users
 * currently logged into the application for the day.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React, { Component } from 'react'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { getColor } from '../../../utils/theming'
import { layout, config } from './utils/chartConfig'
import { getLiveLoginData } from '../../../api/Analytics'
import { logError } from '../../../api/LoggingHelper'

import styles from './LiveLoginTimeSeries.module.scss'

class LiveLoginTimeSeries extends Component {

  constructor(props) {
    super(props)
    this.state = {
      data: undefined,
    }
  }

  componentDidMount = () => {
    this.getTimeSeriesData()
    this.timer = setInterval(this.getTimeSeriesData, 10000)
  }

  componentWillUnmount = () => {
    clearInterval(this.timer)
  }

  getTimeSeriesData = () => {
    getLiveLoginData().then((res) => {
      this.setState({ data: res.data })
    })
      .catch((err) => logError(
        err.toString(),
        err.message,
        'UsersAnalytics.getTimeSeriesData',
        err.stack
      ))
  }

  render() {
    const { data } = this.state
    let traceData = []
    let rangeStart = new Date()
    let rangeFinish = new Date()

    // Set up the Plotly Trace
    if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
      traceData = [
        {
          type: 'scatter',
          mode: 'lines',
          x: data.x,
          y: data.y,
          line: {
            color: getColor('--b300'),
          },
        },
      ]

      const now = Date.now()
      rangeStart = new Date(now)
      rangeFinish.setDate(rangeStart.getDate() - 1)
      // console.log(rangeStart)
      // console.log(rangeFinish)
    }

    if (traceData.length === 0) {
      return <div><p>No data.</p></div>
    }

    return (
      <AutoSizer>
        {({ height, width }) => {

          return (
            <Plot
              data={traceData}
              layout={{
                height,
                width,
                showlegend: false,
                plot_bgcolor: getColor('--n0'),
                paper_bgcolor: getColor('--n0'),
                margin: {
                  t: 56,
                  b: 56,
                  l: 64,
                  r: 64,
                  // pad: 12,
                },
                /*padding: {
                  r: 0,
                },*/
                xaxis: {
                  title: 'Date and Time',
                  titlefont: {
                    family: 'Open Sans',
                    size: 14,
                    color: getColor('--n500'),
                  },
                  tickfont: {
                    family: 'Open Sans',
                    size: 11,
                    weight: 600,
                    color: getColor('--n500'),
                  },
                  autorange: true,
                  type: 'date',
                  // range: [rangeStart, rangeFinish],
                  rangeslider: {
                    range: [rangeStart],
                  },
                  rangeselector: {
                    buttons: [
                      {
                        count: 10,
                        label: '10m',
                        step: 'minute',
                        stepmode: 'backward'
                      },
                      {
                        count: 1,
                        label: '1h',
                        step: 'hour',
                        stepmode: 'backward'
                      },
                      {
                        step: 'all',
                      },
                    ]
                  }
                },
                yaxis: {
                  title: 'Count',
                  titlefont: {
                    family: 'Open Sans',
                    size: 14,
                    color: getColor('--n500'),
                  },
                  tickfont: {
                    family: 'Open Sans',
                    size: 11,
                    weight: 600,
                    color: getColor('--n500'),
                  },
                  autorange: true,
                  type: 'linear',
                },
              }}
              config={{
                modeBarButtonsToRemove: [
                'toImage', 'select2d', 'lasso2d', 'toggleSpikelines',
                'scrollZoom', 'hoverCompareCartesian', 'hoverClosestCartesian',
                'autoScale2d'
                ],
                displaylogo: false,
                displayModeBar: 'hover',
              }}
            />
          )
        }}
      </AutoSizer>
    )
  }
}

export default LiveLoginTimeSeries
