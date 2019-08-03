import {
  GET_ALLOYS,
} from './types'

export const getAlloys = () => (dispatch) => {
  fetch('http://localhost:8001/global/alloys', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: GET_ALLOYS,
          payload: data.alloys,
        })
      }
    })
    .catch(err => console.log(err))
}

export const getAlloy = alloyId => (dispatch) => {
  // get one a alloy
}
