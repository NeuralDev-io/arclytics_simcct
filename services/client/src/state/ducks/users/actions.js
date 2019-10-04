import {
  GET_USERS,
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
          payload: res.data.users || [],
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
