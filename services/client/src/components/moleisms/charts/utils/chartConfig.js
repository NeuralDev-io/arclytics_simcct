import { getColor } from '../../../../utils/theming'

export const layout = (height, width) => ({
  width,
  height,
  showlegend: true,
  legend: {
    x: 0,
    y: -0.3,
    orientation: 'h',
    font: {
      family: 'Open Sans',
      color: getColor('--n900'),
    },
  },
  plot_bgcolor: getColor('--n0'),
  paper_bgcolor: getColor('--n0'),
  margin: {
    t: 32,
    l: 54,
    r: 0,
    pad: 12,
  },
  padding: {
    r: 0,
  },
  xaxis: {
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
  },
  yaxis: {
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
    position: -0.1,
  },
})

export const config = {
  modeBarButtonsToRemove: ['toImage', 'sendDataToCloud', 'select2d', 'lasso2d', 'toggleSpikelines'],
  displaylogo: false,
  displayModeBar: 'hover',
}
