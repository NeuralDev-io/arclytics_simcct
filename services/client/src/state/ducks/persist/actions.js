import {
  GET_USER_PROFILE,
} from './types'

export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  fetch('http://localhost:8000/user', {
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
          type: GET_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}
