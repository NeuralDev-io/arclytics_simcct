import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
  UPDATE_EMAIL,
  CHANGE_PASSWORD,
  SAVE_SIM,
  GET_SIM,
} from './types'
import { addFlashToast } from '../toast/actions'

export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  return fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status !== 200) throw new Error('Couldn\'t retrieve user profile')
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: GET_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}

export const createUserProfile = values => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/profile`, {
    method: 'POST',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status !== 201) throw new Error('Something went wrong')
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: CREATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}

export const updateUserProfile = values => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user`, {
    method: 'PATCH',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status !== 200) throw new Error('Something went wrong')
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}

export const updateEmail = values => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/auth/email/change`, {
    method: 'PUT',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status !== 200) throw new Error('Something went wrong')
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_EMAIL,
          payload: data.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}

export const changePassword = values => (dispatch) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/auth/password/change`, {
    method: 'PUT',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status !== 200) throw new Error('Something went wrong')
      return res.json()
    })
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: CHANGE_PASSWORD,
          payload: data.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}

/**
 * API call to `users` server to save a new saved simulation for the user.
 * User's are identified by the JWT token passed as an Authorization header.
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
  const { grain_size_ASTM, grain_size_diameter, ...others } = configurations
  const validConfigs = {
    ...others,
    grain_size: grain_size_ASTM,
  }

  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/simulation`, {
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
    if (res.status !== 201) throw new Error('Something went wrong')
    return res.json()
  })
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: SAVE_SIM,
          payload: res.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
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
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/simulation`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.status === 404) throw new Error('No saved simulations found')
    if (res.status !== 200) throw new Error('Something went wrong')
    return res.json()
  })
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: GET_SIM,
          payload: res.data,
        })
      }
    })
    .catch(err => addFlashToast({
      message: err.message,
      options: { variant: 'error' },
    }, true)(dispatch))
}
