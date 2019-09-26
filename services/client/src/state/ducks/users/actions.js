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
      if (res.status !== 200) {
        return { status: 'fail', message: 'Couldn\'t retrieve user list' }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        })
      }
      if (res.status === 'success') {
        dispatch({
          type: GET_USERS,
          payload: res.data.users || [],
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      console.log(err)
    })
}

export const updateUser = () => (dispatch) => {

}
