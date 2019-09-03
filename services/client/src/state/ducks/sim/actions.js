import {
  RUN_SIM,
  INIT_SESSION,
  UPDATE_ALLOY_OPTION,
  UPDATE_COMP,
  UPDATE_DILUTION,
  UPDATE_CONFIG_METHOD,
  UPDATE_CONFIG,
  UPDATE_DISPLAY_USER_CURVE,
  UPDATE_CCT_INDEX,
  LOAD_SIM,
} from './types'
import { ASTM2Dia, dia2ASTM } from '../../../utils/grainSizeConverter'

/**
 * Initialise a new sim session on the server, then update alloy in
 * Redux state and use the response to update auto-calculated fields.
 *
 * Call this function to update state when alloy1 or alloy2 is changed.
 * At the moment, only pass in 'single' for option and 'parent' for type.
 *
 * @param {string} option 'single' | 'mix'
 * @param {string} type 'parent' | 'weld'
 * @param {object} alloy alloy to be used
 */
export const initSession = (option, type, alloy) => (dispatch) => {
  dispatch({
    type: INIT_SESSION,
    status: 'started',
  })

  // Only POST the name and compositions to the server,
  // but _id will also be saved to Redux state to refer to
  // the original alloy
  fetch('http://localhost:8001/alloys/update', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy: {
        name: alloy.name,
        compositions: alloy.compositions,
      },
    }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: INIT_SESSION,
          status: 'success',
          config: res.data,
          alloyType: type,
          alloy,
        })
      }
    })
    .catch((err) => {
      dispatch({
        type: INIT_SESSION,
        status: 'fail',
      })
      console.log(err)
    })
}

/**
 * Update alloy option in state.
 *
 * @param {string} option 'single' | 'mix'
 */
export const updateAlloyOption = option => (dispatch) => {
  dispatch({
    type: UPDATE_ALLOY_OPTION,
    payload: option,
  })
}

/**
 * Update alloy in session state. Call this function when alloy
 * composition is changed.
 *
 * @param {string} option 'single' | 'mix'
 * @param {string} type 'parent' | 'weld'
 * @param {object} alloy alloy to be updated
 */
export const updateComp = (option, type, alloy) => (dispatch) => {
  fetch('http://localhost:8001/alloys/update', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy,
    }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: UPDATE_COMP,
          config: res.data,
          alloyType: type,
          alloy,
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateDilution = val => (dispatch) => {
  // calculate mix compositions here

  // now dispatch
  dispatch({
    type: UPDATE_DILUTION,
    payload: val,
  })
}

/**
 * Update CCT/TTT method.
 * @param {string} value new method
 */
export const updateConfigMethod = value => (dispatch) => {
  fetch('http://localhost:8001/configs/method/update', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ method: value }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: UPDATE_CONFIG_METHOD,
          payload: value,
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateGrainSize = (unit, value) => (dispatch) => {
  let newGrainSize = { grain_size_ASTM: '', grain_size_diameter: '' }
  let grainSize = parseFloat(value)
  let isValid = false

  if (value === '') {
    isValid = true
    grainSize = 0
  } else if (unit === 'astm') {
    const converted = ASTM2Dia(grainSize)
    if (!Number.isNaN(converted) && Number.isFinite(converted)) {
      isValid = true
      newGrainSize = {
        grain_size_ASTM: grainSize,
        grain_size_diameter: converted,
      }
    }
  } else if (unit === 'dia') {
    const converted = dia2ASTM(grainSize)
    if (!Number.isNaN(converted) && Number.isFinite(converted)) {
      isValid = true
      newGrainSize = {
        grain_size_ASTM: converted,
        grain_size_diameter: grainSize,
      }
    }
  }

  if (isValid) {
    fetch('http://localhost:8001/configs/update', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Session: localStorage.getItem('session'),
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ grain_size: grainSize }),
    })
      .then(res => res.json())
      .then((res) => {
        if (res.status === 'fail') throw new Error(res.message)
        if (res.status === 'success') {
          dispatch({
            type: UPDATE_CONFIG,
            payload: newGrainSize,
          })
        }
      })
      .catch(err => console.log(err))
  }
}

export const updateMsBsAe = (name, reqBody) => (dispatch) => {
  fetch(`http://localhost:8001/configs/${name}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(reqBody),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: UPDATE_CONFIG,
          payload: reqBody,
        })
      }
    })
    .catch(err => console.log(err))
}

export const getMsBsAe = name => (dispatch) => {
  fetch(`http://localhost:8001/configs/${name}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: UPDATE_CONFIG,
          payload: res.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const setAutoCalculate = (name, value) => (dispatch) => {
  dispatch({
    type: UPDATE_CONFIG,
    payload: {
      [name]: value,
    },
  })
}

export const updateConfig = (name, value) => (dispatch) => {
  fetch('http://localhost:8001/configs/update', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ [name]: value }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') {
        dispatch({
          type: UPDATE_CONFIG,
          payload: { [name]: value },
        })
      }
    })
    .catch(err => console.log(err))
}

export const toggleDisplayUserCurve = value => (dispatch) => {
  dispatch({
    type: UPDATE_DISPLAY_USER_CURVE,
    payload: value,
  })
}

// TODO: Check back of this function
export const runSim = () => (dispatch, getState) => {
  const {
    grain_size_ASTM,
    nucleation_start,
    nucleation_finish,
    cct_cooling_rate,
    start_temp,
  } = getState().sim.configurations

  fetch('http://localhost:8001/configs/update', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      grain_size: grain_size_ASTM,
      nucleation_start,
      nucleation_finish,
      cct_cooling_rate,
      start_temp,
    }),
  }).catch(err => console.log(err))
  fetch('http://localhost:8001/simulate', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(simRes => simRes.json())
    .then((simRes) => {
      if (simRes.status === 'fail') throw new Error(simRes.message)
      if (simRes.status === 'success') {
        dispatch({
          type: RUN_SIM,
          payload: simRes.data,
        })
      }
    })
    .catch(err => console.log(err))
}

export const updateCCTIndex = idx => (dispatch) => {
  dispatch({
    type: UPDATE_CCT_INDEX,
    payload: idx,
  })
}

export const loadSim = sim => (dispatch) => {
  dispatch({
    type: LOAD_SIM,
    payload: sim,
  })
}
