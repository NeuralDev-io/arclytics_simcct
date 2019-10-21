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
import { layout, COLORS, COLORS2, COLORS3 } from './utils/chartConfig'

import styles from './Chart.module.scss'

const SavedAlloysByNameHorizontalChart = ({ data }) => {
  let traceData = []

  if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
    let colorscale = COLORS
    if (Array(data.colors).length > COLORS.length) {
      colorscale = (Array(data.colors).length > COLORS2.length) ? COLORS3 : COLORS2
    }
    traceData = [
      {
        type: 'bar',
        x: data.x,
        y: data.y,
        marker: {
          color: data.colors.map(i => {
            const idx = i % colorscale.length
            return colorscale[idx]
          }),
          // color: data.colors
        },
        orientation: 'h',
        opacity: 0.7,
        textfont: {
          family: 'Open Sans',
          size: 16,
        },
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
          showlegend: false,
        }
        return (
          <Plot
            data={traceData}

            layout={{
              ...profileLayout,
              xaxis: {
                ...profileLayout.xaxis,
                title: 'Count',
                gridwidth: 0,
              },
              yaxis: {
                ...profileLayout.yaxis,
                tickangle: 45,
                ticksuffix: '  ', // give it a bit of space to the edge
                position: -1,
                title: 'Alloy names',
                type: 'category'
              },
              margin: {
                t: 45,
                l: 100,
                r: 0,
                pad: 12,
              },
            }}

            config={{
              modeBarButtonsToRemove: [
                'toImage', 'sendDataToCloud', 'select2d', 'lasso2d', 'toggleSpikelines',
                'scrollZoom', 'hoverCompareCartesian', 'hoverClosestCartesian', 'autoScale2d'
              ],
              // editable: false,
              displaylogo: false,
              displayModeBar: 'hover',
              showTips: true,
            }}
          />
        )
      }}
    </AutoSizer>
  )
}

SavedAlloysByNameHorizontalChart.propTypes = {
  data: PropTypes.shape({
    x: PropTypes.arrayOf(PropTypes.string),
    y: PropTypes.arrayOf(PropTypes.number),
    colors: PropTypes.arrayOf(PropTypes.number),
  }),
}

SavedAlloysByNameHorizontalChart.defaultProps = {
  data: undefined,
}

export default SavedAlloysByNameHorizontalChart
