import { getColor } from '../../../../utils/theming'

/*
* Extended palette colours with 1 shade from 500
* */
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
  '#404041',
]

/*
* Extended palette colours with 2 shades from 500, 700
* */
// noinspection JSUnusedGlobalSymbols
export const COLORS2 = [
  '#d96060', '#d13d3d',
  '#e78c3d', '#e27312',
  '#a0ae49', '#8b9c21',
  '#59ab59', '#349834',
  '#47acb8', '#1e9aa8',
  '#438fc4', '#1a76b7',
  '#7b68d9', '#5e47d1',
  '#9b5eba', '#853bab',
  '#c354b1', '#b62fa0',
  '#a1746b', '#8c564b',
  '#555556', '#404041',
]

/*
* Extended palette colours with 3 shades from 300, 500, 700
* */
export const COLORS3 = [
  '#d96060', '#d13d3d', '#AB3232',
  '#e78c3d', '#e27312', '#B95E0F',
  '#a0ae49', '#8b9c21', '#72801B',
  '#59ab59', '#349834', '#2B7D2B',
  '#47acb8', '#1e9aa8', '#197E8A',
  '#438fc4', '#1a76b7', '#156196',
  '#7b68d9', '#5e47d1', '#4D3AAB',
  '#9b5eba', '#853bab', '#6D308C',
  '#c354b1', '#b62fa0', '#952783',
  '#a1746b', '#8c564b', '#73473E',
  '#7e7f80', '#555556', '#404041',
]

/*
* Extended palette colours with 4 shades from 300, 400, 500, 700
* */
// noinspection JSUnusedGlobalSymbols
export const COLORS4 = [
  '#d96060', '#d54e4e', '#d13d3d', '#AB3232',
  '#e78c3d', '#e58027', '#e27312', '#B95E0F',
  '#a0ae49', '#95a535', '#8b9c21', '#72801B',
  '#59ab59', '#46a146', '#349834', '#2B7D2B',
  '#47acb8', '#32a3b0', '#1e9aa8', '#197E8A',
  '#438fc4', '#2f82bd', '#1a76b7', '#156196',
  '#7b68d9', '#5d4db3', '#5e47d1', '#4D3AAB',
  '#9b5eba', '#904db3', '#853bab', '#6D308C',
  '#c354b1', '#bd42a9', '#b62fa0', '#952783',
  '#a1746b', '#96655b', '#8c564b', '#73473E',
  '#a3a4a5', '#7e7f80', '#555556', '#404041',
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
    color: getColor('--n500'),
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
    color: getColor('--n500'),
    position: -0.1,
  },
})

export const config = {
  modeBarButtonsToRemove: ['toImage', 'sendDataToCloud', 'select2d', 'lasso2d', 'toggleSpikelines'],
  displaylogo: false,
  displayModeBar: 'hover',
}
