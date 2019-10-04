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

const ProfileBarChart = ({ data }) => {
  let chartData = []
  if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
    chartData = [
      {
        x: data,
        y: data,
        name: '',
        type: 'scatter',
        mode: 'bar',
        line: {
          // TODO(andrew@neuraldev.io): Make this dynamic enough to change colours
          color: getColor('--br500'),
          shape: 'spline',
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
        // TODO(andrew@neuraldev.io): Add more layout configs if needed
        const profileLayout = { ...defaultLayout }
        return (
          <Plot
            data={chartData}
            layout={{
              ...profileLayout,
              xaxis: {
                ...profileLayout.xaxis,
                title: '',
                type: '',
              },
              yaxis: {
                ...profileLayout.yaxis,
                title: '',
                type: '',
              },
            }}
            config={config}
          />
        )
      }}
    </AutoSizer>
  )
}

ProfileBarChart.propTypes = {
  // TODO(andrew@neuraldev.io): Check the data again.
  data: PropTypes.shape({}),
}

ProfileBarChart.defaultProps = {
  data: undefined,
}

export default ProfileBarChart
