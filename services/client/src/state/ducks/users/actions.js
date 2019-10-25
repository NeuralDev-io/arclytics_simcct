import {
  GET_USERS,
  SEARCH_USERS,
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
export const getUsers = params => (dispatch) => {
  // Ensure redux knows we have started the retrieval so it waits to render
  dispatch({
    type: GET_USERS,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}/users/query?${params}`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 404) {
        return {
          status: 'success',
          data: [],
        }
      }
      if (res.status === 401) {
        return {
          status: 'fail',
          message: 'Not Authorized.',
        }
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          // Toast error message
          message: 'Get users not successful.',
        }
      }
      // Success
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        })(dispatch)
        dispatch({
          type: GET_USERS,
          status: 'fail',
        })
      }
      if (res.status === 'success') {
        dispatch({
          type: GET_USERS,
          status: 'success',
          payload: res || {},
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.getUsers', err.stack)
    })
}


export const searchUsers = params => (dispatch) => {
  // Ensure redux knows we have started the retrieval so it waits to render
  dispatch({
    type: SEARCH_USERS,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}/users/search?${params}`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 404) {
        // Ensure the 404 returned is not an error but just a successful
        // request without any data returned.
        return {
          status: 'success',
          data: [],
        }
      }
      if (res.status === 401) {
        return {
          status: 'fail',
          message: 'Not Authorized.',
        }
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          // Toast error message
          message: 'Search not successful.',
        }
      }
      // success
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        })(dispatch)
        dispatch({
          type: SEARCH_USERS,
          status: 'fail',
        })
      }
      if (res.status === 'success') {
        dispatch({
          type: SEARCH_USERS,
          status: 'success',
          payload: res || {},
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.searchUsers', err.stack)
    })
}

export const deactivateUser = (email) => (dispatch) => {
  fetch(`${SIMCCT_URL}/disable/user`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
    }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong while deactivating user',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'success') {
        addFlashToast({
          message: res.message,
          options: { variant: 'success' },
        }, true)(dispatch)
        dispatch({
          type: DEACTIVATE_USER,
        })
      }
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.deactivateUser', err.stack)
    })
}

export const enableUser = (email) => (dispatch) => {
  fetch(`${SIMCCT_URL}/enable/user`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
    }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong activating user',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'success') {
        dispatch({
          type: ENABLE_USER,
          payload: email,
        })
      }
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.enableUser', err.stack)
    })
}

export const promoteAdmin = (email, position) => (dispatch) => {
  fetch(`${SIMCCT_URL}/admin/create`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: (JSON.stringify({
      email,
      position,
    })),
  })
    .then((res) => {
      if (res.status !== 202) {
        return {
          status: 'fail',
          message: 'Something went wrong when promoting user',
        }
      }
      return res.json()
    })
    .then((res) => {
      // check response
      if (res.status === 'success') {
        dispatch({
          type: PROMOTE_ADMIN,
          payload: {
            email,
            position,
          },
        })
      }
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'users.actions.promoteAdmin', err.stack)
    })
}
