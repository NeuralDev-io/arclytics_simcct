/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * This component is a generic stateless `react-plotly` wrapper that will be used
 * to display the Plotly Mapbox Density map.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import AutoSizer from 'react-virtualized-auto-sizer'
import { getColor } from '../../../utils/theming'
import { InlineSpinner } from '../../elements/spinner'

import styles from './LoginLocationMapbox.module.scss'

const LoginLocationMapbox = ({
  token,
  data,
  mapBoxStyle,
  colorScale,
  isLoading,
}) => {
  let traceData = []
  if (data !== undefined && data !== null && Object.keys(data).length !== 0) {
    traceData = [
      {
        type: 'densitymapbox',
        lon: data.longitude,
        lat: data.latitude,
        z: data.count,
        radius: 15,
        text: data.count.map(String),
        colorscale: colorScale,
        colorbar: {
          thickness: 15,
          xpad: 5,
          ypad: 15,
          bgcolor: getColor('--n0'),
          tickfont: {
            family: 'Open Sans',
            size: 11,
            weight: 6000,
            color: getColor('--n500')
          }
        },
      },
    ]
  }

  if (traceData.length === 0) {
    if (isLoading) {
      return <div className={styles.noData}>
        <InlineSpinner />
      </div>
    }
    return <div className={styles.noData}>No data.</div>
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
              mapbox: {
                style: mapBoxStyle,
                center: {
                  lon: 140,
                  lat: -15
                },
                zoom: 2,
              },
              plot_bgcolor: getColor('--n0'),
              paper_bgcolor: getColor('--n0'),
              margin: {
                t: 0,
                l: 0,
                r: 0,
                b: 0,
              },
              pad: 0,
            }}

            config={{
              mapboxAccessToken: token,
              modeBarButtonsToRemove: [
                'select2d', 'lasso2d', 'toggleSpikelines',
                'hoverCompareCartesian', 'hoverClosestCartesian',
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

LoginLocationMapbox.propTypes = {
  data: PropTypes.shape({
    latitude: PropTypes.arrayOf(PropTypes.number),
    longitude: PropTypes.arrayOf(PropTypes.number),
    count: PropTypes.arrayOf(PropTypes.number),
  }),
}

LoginLocationMapbox.defaultProps = {
  data: undefined,
}

export default LoginLocationMapbox
