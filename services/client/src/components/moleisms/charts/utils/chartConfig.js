import colours from '../../../../styles/_colors_light.scss'

export const layout = (width, height) => ({
  width,
  height,
  showlegend: true,
  legend: { x: 0, y: 1.25, orientation: 'h' },
  plot_bgcolor: colours.n0,
  paper_bgcolor: colours.n0,
  margin: {
    t: 0,
    pad: 8,
  },
})

export const config = {
  modeBarButtonsToRemove: ['toImage', 'sendDataToCloud', 'select2d', 'lasso2d', 'toggleSpikelines'],
  displaylogo: false,
  displayModeBar: 'hover',
}
