import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
  UPDATE_EMAIL,
  CHANGE_PASSWORD,
  SAVE_SIM,
  GET_SIM,
  GET_LAST_SIM,
} from './types'
import { SIMCCT_URL } from '../../../constants'
import { addFlashToast } from '../toast/actions'
import { logError } from '../../../api/LoggingHelper'

export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  return fetch(`${SIMCCT_URL}/user`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
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
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.updateUserProfile', err.stack)
    })
}

export const updateEmail = values => (dispatch) => {
  fetch(`${SIMCCT_URL}/auth/email/change`, {
    method: 'PUT',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Email was not saved',
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
          type: UPDATE_EMAIL,
          payload: data.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.updateEmail', err.stack)
    })
}

export const changePassword = values => (dispatch) => {
  fetch(`${SIMCCT_URL}/auth/password/change`, {
    method: 'PUT',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong. Password was not updated',
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
          type: CHANGE_PASSWORD,
          payload: data.data,
        })
      }
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
  fetch(`${SIMCCT_URL}/user/simulation`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
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
      }
      if (res.status === 'success') {
        dispatch({
          type: GET_SIM,
          payload: res.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'self.actions.getSavedSimulations', err.stack)
    })
}

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

  fetch(`${SIMCCT_URL}/user/last/simulation`, {
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

export const getLastSim = () => dispatch => (
  fetch(`${SIMCCT_URL}/user/last/simulation`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then(res => res.json())
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
