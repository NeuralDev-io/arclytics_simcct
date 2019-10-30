import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
  UPDATE_EMAIL,
  SAVE_SIM,
  GET_SIM,
  GET_LAST_SIM,
  DELETE_SIM,
  CHANGE_THEME,
  UPDATE_PASSWORD,
  DELETE_ACCOUNT,
  DOWNLOAD_ACCOUNT_DATA,
} from './types'
import { SIMCCT_URL } from '../../../constants'
import { addFlashToast } from '../toast/actions'
import { logError } from '../../../api/LoggingHelper'
import { changeTheme } from '../../../utils/theming'
import { addLocation, forceSignIn } from '../redirector/actions'

/**
 * Make API request to retrieve user profile.
 */
export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  return fetch(`${SIMCCT_URL}/user`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Couldn\'t load profile',
        }
      }
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') {
        addFlashToast({
          message: data.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (data.status === 'success') {
        dispatch({
          type: GET_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.getUserProfile', err.stack)
    })
}

/**
 * Post user profile to the API
 * @param {any} values user profile object
 */
export const createUserProfile = values => (dispatch) => {
  fetch(`${SIMCCT_URL}/user/profile`, {
    method: 'POST',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 201) {
        return {
          status: 'fail',
          message: 'Something went wrong. Profile was not saved',
        }
      }
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') {
        addFlashToast({
          message: data.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (data.status === 'success') {
        dispatch({
          type: CREATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.createUserProfile', err.stack)
    })
}

/**
 * Update user profile
 * @param {any} values user profile object
 */
export const updateUserProfile = values => (dispatch) => {
  fetch(`${SIMCCT_URL}/user`, {
    method: 'PATCH',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Profile was not saved',
        }
      }
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') {
        addFlashToast({
          message: data.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_USER_PROFILE,
          payload: data.data,
        })
        addFlashToast({
          message: 'Profile updated',
          options: { variant: 'success' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.updateUserProfile', err.stack)
    })
}

/**
 * Update user email
 * @param {string} email new email
 */
export const updateEmail = email => (dispatch) => {
  dispatch({
    type: UPDATE_EMAIL,
    status: 'started',
  })

  return fetch(`${SIMCCT_URL}/auth/email/change`, {
    method: 'PUT',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ new_email: email }),
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Make sure you use a valid email.',
        }
      }
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') {
        addFlashToast({
          message: data.message,
          options: { variant: 'error' },
        }, true)(dispatch)
        dispatch({
          type: UPDATE_EMAIL,
          status: 'fail',
        })
      }
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_EMAIL,
          payload: email,
          status: 'success',
        })
        addFlashToast({
          message: 'Email updated. Please verify your new email.',
          options: { variant: 'success' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.updateEmail', err.stack)
    })
}

/**
 * Update user password
 * @param {any} values object containing password fields
 */
export const changePassword = (password, passwordConfirm) => (dispatch) => {
  dispatch({
    type: UPDATE_PASSWORD,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}/auth/password/change`, {
    method: 'PUT',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      new_password: password,
      confirm_password: passwordConfirm,
    }),
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Password was not updated',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        addFlashToast({
          message: 'Password updated successfully',
          options: { variant: 'success' },
        }, true)(dispatch)
      }
      dispatch({
        type: UPDATE_PASSWORD,
        status: 'finished',
      })
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.changePassword', err.stack)
    })
}

/**
 * API call to `users` server to save a new saved simulation for the user.
 * This function will only be called when the configurations are valid
 * and the simulation has been run
 */
export const saveSimulation = () => (dispatch, getState) => {
  // first, get sim alloys and configs from state
  const { configurations, alloys, results } = getState().sim

  const alloyStore = {
    alloy_option: alloys.alloyOption,
    alloys: {
      parent: alloys.parent,
      /*
      * DECISION: We will not implement this as it adds too much complexity to
      * the logical path of the system state. This was not a core requirement
      * and Dr. Bendeich often said he did not want this implemented at all.
      * */
      weld: null,
      mix: null,
    },
  }
  const simResults = {
    USER: results.USER,
    CCT: results.CCT,
    TTT: results.TTT,
  }

  // eslint-disable-next-line camelcase
  const {
    grain_size_ASTM,
    grain_size_diameter,
    error,
    ...others
  } = configurations
  const validConfigs = {
    ...others,
    grain_size: grain_size_ASTM,
  }

  fetch(`${SIMCCT_URL}/user/simulation`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      configurations: validConfigs,
      alloy_store: alloyStore,
      simulation_results: simResults,
    }),
  }).then((res) => {
    if (res.status === 401) {
      forceSignIn()(dispatch)
      throw new Error('Session expired')
    }
    if (res.status !== 201) {
      return {
        status: 'fail',
        message: 'Something went wrong. Simulation was not saved',
      }
    }
    return res.json()
  })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        dispatch({
          type: SAVE_SIM,
          payload: res.data,
        })
        addFlashToast({
          message: 'Simulation saved',
          options: { variant: 'success' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.saveSimulation', err.stack)
    })
}

/**
 * API call to `users` server to retrieve the user's list of saved simulations.
 * Returns a list of saved simulations as an `application/json` content-type
 * with the following schema:
 *
 * {
 *    "status": "success",
 *    "data": [
 *      {"_id": "ObjectId", "configurations": {...}, "alloy_store": {...}},
 *      {...},
 *      {...}
 *    ]
 * }
 */
export const getSavedSimulations = () => (dispatch) => {
  dispatch({
    type: GET_SIM,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}/user/simulation`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.status === 401) {
      forceSignIn()(dispatch)
      throw new Error('Session expired')
    }
    if (res.status === 404) { return { status: 'success', data: [] } }
    if (res.status !== 200) {
      return {
        status: 'fail',
        message: 'Couldn\'t retrieve saved simulations',
      }
    }
    return res.json()
  })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
        dispatch({
          type: GET_SIM,
          status: 'fail',
        })
      }
      if (res.status === 'success') {
        dispatch({
          type: GET_SIM,
          status: 'success',
          payload: res.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.getSavedSimulations', err.stack)
    })
}

/**
 * API call to `users` server to retrieve the user's list of saved simulations.
 * Returns a list of saved simulations as an `application/json` content-type
 * with the following schema:
 *
 * {
 *    "status": "success",
 *    "data": [
 *      {"_id": "ObjectId", "configurations": {...}, "alloy_store": {...}},
 *      {...},
 *      {...}
 *    ]
 * }
 */
export const deleteSavedSimulation = id => (dispatch) => (
  fetch(`${SIMCCT_URL}/user/simulation/${id}`, {
    method: 'DELETE',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.status === 401) {
      forceSignIn()(dispatch)
      throw new Error('Session expired')
    }
    if (res.status === 404) {
      return {
        status: 'fail',
        message: 'This simulation no longer exists in your account',
      }
    }
    if (res.status !== 202) {
      return {
        status: 'fail',
        message: 'Couldn\'t delete this simulation',
      }
    }
    return res.json()
  })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        addFlashToast({
          message: 'Simulation deleted',
          options: { variant: 'success' },
        }, true)(dispatch)
        dispatch({
          type: DELETE_SIM,
          payload: id,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.deleteSavedSimulation', err.stack)
    })
)

/**
 * Save the current sim to a user in the backend.
 * This function is called before a user logs out, so the next time they
 * log in, the sim can be loaded up and the user can continue where
 * they left off.
 */
export const saveLastSim = () => (dispatch, getState) => {
  // first, get sim alloys and configs from state
  const { configurations, alloys, results } = getState().sim
  const alloyStore = {
    alloy_option: alloys.alloyOption,
    alloys: {
      parent: alloys.parent,
      // TODO(daltonle): Change this when weld and mix are added
      weld: alloys.parent,
      mix: alloys.parent,
    },
  }
  const simResults = {
    USER: results.USER,
    CCT: results.CCT,
    TTT: results.TTT,
  }

  // eslint-disable-next-line camelcase
  const {
    grain_size_ASTM,
    grain_size_diameter,
    error,
    ...others
  } = configurations
  const validConfigs = {
    ...others,
    grain_size: grain_size_ASTM,
  }

  const alloyError = alloys.parentError
  const configError = configurations.error

  const isValid = Object.keys(alloyError).length !== 0 && Object.keys(configError) !== 0

  return fetch(`${SIMCCT_URL}/user/last/simulation`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      is_valid: isValid,
      configurations: validConfigs,
      alloy_store: alloyStore,
      simulation_results: simResults,
      invalid_fields: {
        invalid_alloy_store: alloyError,
        invalid_configs: configError,
      },
    }),
  })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.saveLastSim', err.stack)
    })
}

/**
 * Get the last sim saved to a user in the backend
 */
export const getLastSim = () => dispatch => (
  fetch(`${SIMCCT_URL}/user/last/simulation`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status === 404) { return { status: 'fail', data: {} } }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Couldn\'t retrieve saved simulations',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'success') {
        dispatch({
          type: GET_LAST_SIM,
          payload: res.data,
        })
      }
      return res
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.getLastSim', err.stack)
    })
)

/**
 * Change theme variable in Redux store so that logo components can be
 * updated across the app
 * @param {string} theme new theme name
 */
export const changeThemeRedux = theme => (dispatch) => {
  localStorage.setItem('theme', theme)
  dispatch({
    type: CHANGE_THEME,
    payload: theme,
  })
  changeTheme(theme)
}


export const downloadAccountData = () => (dispatch) => {
  dispatch({
    type: DOWNLOAD_ACCOUNT_DATA,
    status: 'started',
  })

  return fetch(`${SIMCCT_URL}/user/data`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Please try again',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        })(dispatch)
      }
      dispatch({
        type: DOWNLOAD_ACCOUNT_DATA,
        status: 'finished',
      })
      return res
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.downloadAccountData', err.stack)
    })
}

/**
 * Delete user account. After account is deleted, redirect back
 * to /signin
 */
export const deleteAccount = () => (dispatch) => {
  dispatch({
    type: DELETE_ACCOUNT,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}/auth/user`, {
    method: 'DELETE',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status === 401) {
        forceSignIn()(dispatch)
        throw new Error('Session expired')
      }
      if (res.status !== 204) {
        return {
          status: 'fail',
          message: 'Something went wrong. Please try again',
        }
      }
      if (res.status === 204) {
        return {
          status: 'success',
        }
      }
      return {}
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        })(dispatch)
        dispatch({
          type: DELETE_ACCOUNT,
          status: 'fail',
        })
      }
      if (res.status === 'success') {
        addLocation({
          pathname: '/signin',
          state: {
            accountDeleted: true,
          },
        })(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.deleteAccount', err.stack)
    })
}
