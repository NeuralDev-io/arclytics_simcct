import {
  GET_USERS,
} from './types'
import { addFlashToast } from '../toast/actions'

export const getUsers = () => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/users`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status !== 200) throw new Error('Something went wrong')
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: GET_USERS,
          payload: res.data.users || [],
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}

export const updateUser = () => (dispatch) => {

}
