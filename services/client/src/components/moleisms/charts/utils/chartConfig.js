import { getColor } from '../../../../utils/theming'

export const COLORS = [
  '#d96060',
  '#e78c3d',
  '#a0ae49',
  '#59ab59',
  '#47acb8',
  '#438fc4',
  '#7b68d9',
  '#9b5eba',
  '#c354b1',
  '#a1746b',
  '#404041'
]

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
