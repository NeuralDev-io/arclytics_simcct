import { GET_PERSIST_USER_STATUS } from './types'

// MOVED TO src/state/ducks/self
// export const getUserProfile = () => (dispatch) => {}
// export const createUserProfile = values => (dispatch) => {}
// export const updateUserProfile = values => (dispatch) => {}

export const getPersistUserStatus = () => (dispatch) => { // eslint-disable-line
  return fetch(`${process.env.REACT_APP_USER_HOST}/auth/status`, {
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
          type: GET_PERSIST_USER_STATUS,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}
