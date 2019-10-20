/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * This component is a generic stateless `react-plotly` wrapper that will be used
 * to display the Plotly Bar charts of User Profile answers.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { layout, config } from './utils/chartConfig'
import { getColor } from '../../../utils/theming'

import styles from './ProfileBarChart.module.scss'

const ProfileBarChart = ({ title, name, data, color }) => {
  let traceData = []
  if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
    traceData = [
      {
        type: 'bar',
        x: data.x,
        y: data.y,
        name: name,
        text: data.y.map(String),
        textposition: 'inside',
        hoverinfo: 'none',
        marker: {
          color: getColor(color)
        },
        opacity: 0.7,
        textfont: {
          family: 'Open Sans',
          size: 16,
          // color: getColor('--arc500')
        }
      },
    ]
  }

  if (traceData.length === 0) {
    return <div className={styles.noData}>No data.</div>
  }

  return (
    <AutoSizer>
      {({ height, width }) => {
        const defaultLayout = { ...layout(height, width) }
        const profileLayout = {
          ...defaultLayout,
          showlegend: false
        }
        return (
          <Plot
            data={traceData}

            layout={{
              ...profileLayout,
              title: title,
              xaxis: {
                ...profileLayout.xaxis,
              },
              yaxis: {
                ...profileLayout.yaxis,
                title: 'Number of Answers',
                gridwidth: 0
              },
            }}

            config={{
              modeBarButtonsToRemove: [
                'toImage', 'sendDataToCloud', 'select2d', 'lasso2d', 'toggleSpikelines',
                'scrollZoom', 'hoverCompareCartesian', 'hoverClosestCartesian', 'autoScale2d'
              ],
              staticPlot: true,
              editable: false,
              displaylogo: false,
              displayModeBar: 'hover',
              showTips: true
            }}
          />
        )
      }}
    </AutoSizer>
  )
}

ProfileBarChart.propTypes = {
  data: PropTypes.shape({
    x: PropTypes.arrayOf(PropTypes.string),
    y: PropTypes.arrayOf(PropTypes.number)
  }),
}

ProfileBarChart.defaultProps = {
  data: undefined,
}

export default ProfileBarChart
