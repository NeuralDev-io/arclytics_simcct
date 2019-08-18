import {
  RUN_SIM,
} from './types'

export const runSim = () => (dispatch) => {
  fetch('http://localhost:8001/simulate', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: RUN_SIM,
          payload: res.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const getAlloy = alloyId => (dispatch) => {
  // get one a alloy
}
