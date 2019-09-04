import {
  GET_USERS,
} from './types'

export const getUsers = () => (dispatch) => {
  fetch(`${process.env.REACT_APP_USER_HOST}/users`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: GET_USERS,
          payload: res.data.users || [],
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateUser = () => (dispatch) => {

}
