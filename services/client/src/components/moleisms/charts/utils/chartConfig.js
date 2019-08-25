import { getColor } from '../../../../utils/theming'

export const layout = (height, width) => ({
  width,
  height,
  showlegend: true,
  legend: {
    x: 0,
    y: -0.25,
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
    l: 36,
    r: 0,
    pad: 12,
  },
  padding: {
    r: 0,
  },
})

export const config = {
  modeBarButtonsToRemove: ['toImage', 'sendDataToCloud', 'select2d', 'lasso2d', 'toggleSpikelines'],
  displaylogo: false,
  displayModeBar: 'hover',
}
