import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
  UPDATE_EMAIL,
  CHANGE_PASSWORD,
  SAVE_SIM,
  GET_SIM,
} from './types'

export const getUserProfile = () => (dispatch) => { // eslint-disable-line
  return fetch('http://localhost:8000/user', {
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
          type: GET_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const createUserProfile = values => (dispatch) => {
  fetch('http://localhost:8000/user/profile', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: CREATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateUserProfile = values => (dispatch) => {
  fetch('http://localhost:8000/user', {
    method: 'PATCH',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_USER_PROFILE,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateEmail = values => (dispatch) => {
  fetch('http://localhost:8000/auth/email/change', {
    method: 'PUT',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: UPDATE_EMAIL,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const changePassword = values => (dispatch) => {
  fetch('http://localhost:8000/auth/password/change', {
    method: 'PUT',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') {
        dispatch({
          type: CHANGE_PASSWORD,
          payload: data.data,
        })
      }
    })
    .catch(err => console.log(err))
}

/**
 * API call to `users` server to save a new saved simulation for the user.
 * User's are identified by the JWT token passed as an Authorization header.
 */
export const saveSimulation = () => (dispatch, getState) => {
  // first, get sim alloys and configs from state
  const { configurations, alloys } = getState().sim
  const alloyStore = {
    alloy_option: alloys.alloyOption,
    alloys: {
      parent: alloys.parent,
      // TODO(daltonle): Change this when weld and mix are added 
      weld: alloys.parent,
      mix: alloys.parent,
    },
  }

  // eslint-disable-next-line camelcase
  const { grain_size_ASTM, grain_size_diameter, ...others } = configurations
  const validConfigs = {
    ...others,
    grain_size: grain_size_ASTM,
  }

  fetch('http://localhost:8000/user/simulation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      configurations: validConfigs,
      alloy_store: alloyStore,
    }),
  }).then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: SAVE_SIM,
          payload: res.data,
        })
      }
    })
    // eslint-disable-next-line no-console
    .catch(err => console.log(err))
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
  fetch('http://localhost:8000/user/simulation', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  }).then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: GET_SIM,
          payload: res.data,
        })
      }
    })
    // eslint-disable-next-line no-console
    .catch(err => console.log(err))
}
