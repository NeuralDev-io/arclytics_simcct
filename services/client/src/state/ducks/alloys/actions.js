import {
  GET_ALLOYS,
} from './types'

export const getAlloys = () => (dispatch) => {
  // api call
  const alloys = [
    {
      name: 'Stainless steel',
      compositions: [
        { name: 'Carbon', symbol: 'C', weight: 0.004 },
        { name: 'Mag', symbol: 'Mg', weight: 0.004 },
      ],
    },
  ]
  dispatch({
    type: GET_ALLOYS,
    payload: alloys,
  })
}

export const getAlloy = alloyId => (dispatch) => {
  // get one a alloy
}
