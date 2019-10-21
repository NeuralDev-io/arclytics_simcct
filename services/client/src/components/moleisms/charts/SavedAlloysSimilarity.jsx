/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Saved Alloys Similarity t-SNE chart.
 * This component takes in data passed in from an analysis of Saved Alloy
 * compositions using the t-SNE dimensionality reduction method. It then
 * plots this data on a Cartesian 2-D plane.
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */
import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { InlineSpinner } from '../../elements/spinner'
import { layout, config, COLORS3 } from './utils/chartConfig'
import { getColor } from '../../../utils/theming'

import styles from './Chart.module.scss'

const SavedAlloysSimilarity = ({ data, isLoading }) => {
  let chartData = []

  if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
    const colorLen = Array(COLORS3).length
    chartData = [
      {
        x: data.x,
        y: data.y,
        text: data.label,
        type: 'scatter',
        mode: 'markers',
        marker: {
          size: 8,
          // Cycle through the 3 shades of color for each point.
          color: data.color.map(i => {
            const idx = i % colorLen
            return COLORS3[idx]
          }),
        },
        opacity: 0.75,
        textfont: {
          family: 'Open Sans',
          size: 11,
          weight: 600,
          color: getColor('--n500'),
        },
      },
    ]
  }

  if (chartData.length === 0) {
    if (isLoading) {
      return (
        <div className={styles.noData}>
          <InlineSpinner />
        </div>
      )
    }
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
                title: 'X',
                autorange: true,
              },
              yaxis: {
                ...defaultLayout.yaxis,
                title: 'Y',
                autorange: true,
              },
              showlegend: false,
              plot_bgcolor: getColor('--n0'),
              paper_bgcolor: getColor('--n0'),
              margin: {
                t: 56,
                b: 56,
                l: 64,
                r: 64,
              },
            }}
            config={config}
          />
        )
      }}
    </AutoSizer>
  )
}

SavedAlloysSimilarity.propTypes = {
  data: PropTypes.shape({
    x: PropTypes.arrayOf(PropTypes.number),
    y: PropTypes.arrayOf(PropTypes.number),
    label: PropTypes.arrayOf(PropTypes.string),
    color: PropTypes.arrayOf(PropTypes.number),
  }),
  isLoading: PropTypes.bool.isRequired,
}

SavedAlloysSimilarity.defaultProps = {
  data: undefined,
}

export default SavedAlloysSimilarity
