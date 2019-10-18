import {
  GET_USERS,
  PROMOTE_ADMIN,
  DEACTIVATE_USER,
  ENABLE_USER,
} from './types'
import { SIMCCT_URL } from '../../../constants'
import { addFlashToast } from '../toast/actions'
import { logError } from '../../../api/LoggingHelper'

/**
 * Get a list of users.
 * This function is only available if the current user is an admin.
 */
export const getUsers = () => (dispatch) => {
  fetch(`${SIMCCT_URL}/users`, {
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
          payload: res.data || [],
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.getUsers', err.stack)
    })
}

export const updateUser = () => (dispatch) => {

}

export const deactivateUser = (email) => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/v1/sim/disable/user`,{
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type' : 'application/json'
    },
    body: JSON.stringify({
      email: email
    })
  })
    .then((res) => {
      console.log(res.status)
      dispatch({
        type: DEACTIVATE_USER
      })
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.deactivateUser', err.stack)
    })
}

export const enableUser = (email) => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT.env.REACT_APP_SIM_PORT}/v1/sim/enable/user`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type' : 'application/json'
    },
    body: JSON.stringify({
      email:email,
    })
  })
    .then((res) => {
      console.log(res.status)
      dispatch({
        type: ENABLE_USER
      })
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.enableUser', err.stack)
    })

}

export const promoteAdmin = (email) => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/v1/sim/admin/create`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: (JSON.stringify({
      email: email,
      position: 'Site Administrator',
    }))
  })
    .then((res) => {
      //check response
      if (res.status === 202){
        console.log('response successful')
      }
      else{
        console.log('unsuccessful')
      }
    })
}
