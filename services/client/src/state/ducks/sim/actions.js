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
  LOAD_PERSISTED_SIM,
} from './types'
import { ASTM2Dia } from '../../../utils/grainSizeConverter'
import { addFlashToast } from '../toast/actions'

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
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/alloys/update`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
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
    .then((res) => {
      if (res.status !== 201) {
        return {
          status: 'fail',
          message: 'Something went wrong',
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
      // log to fluentd
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
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/alloys/update`, {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy,
    }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong',
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
          type: UPDATE_COMP,
          config: res.data,
          alloyType: type,
          alloy,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      console.log(err)
    })
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
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/method/update`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ method: value }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong',
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
          type: UPDATE_CONFIG_METHOD,
          payload: value,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      console.log(err)
    })
}

export const updateGrainSize = (astm, dia, grainSizeError) => (dispatch, getState) => {
  const { error } = getState().sim.configurations
  const newGrainSize = { grain_size_ASTM: astm, grain_size_diameter: dia }

  if (Object.keys(grainSizeError).length === 0 && grainSizeError.constructor === Object) {
    delete error.astm
    delete error.dia
  }

  // update grain size value in redux store
  dispatch({
    type: UPDATE_CONFIG,
    payload: {
      error: {
        ...error,
        ...grainSizeError,
      },
      ...newGrainSize,
    },
  })

  // only update to server when the grain size is valid
  if (Object.keys(grainSizeError).length === 0 && grainSizeError.constructor === Object) {
    fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/update`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ grain_size: parseFloat(astm) }),
    })
      .then((res) => {
        if (res.status !== 202) {
          return {
            status: 'fail',
            message: 'Something went wrong',
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
      })
      .catch((err) => {
        // log to fluentd
        console.log(err)
      })
  }
}

export const updateMsBsAe = (name, field, data, valError) => (dispatch, getState) => {
  const { error } = getState().sim.configurations

  // parse values into floats
  const reqBody = {}
  Object.keys(data).forEach((key) => { reqBody[key] = parseFloat(data[key]) })

  // remove error from store error
  if (Object.keys(valError).length === 0 && valError.constructor === Object) {
    if (field === '') {
      // if field is empty string, it means all values are updated with autocalculated data
      // hence there should be no errors
      if (name === 'ms') {
        delete error.ms_temp
        delete error.ms_rate_param
      }
      if (name === 'bs') {
        delete error.bs_temp
      }
      if (name === 'ae') {
        delete error.ae1_temp
        delete error.ae3_temp
      }
    } else delete error[field]
  }

  // update config in redux store
  dispatch({
    type: UPDATE_CONFIG,
    payload: {
      error: {
        ...error,
        ...valError,
      },
      ...data,
    },
  })

  // only send update to server when there is no error
  if (Object.keys(valError).length === 0 && valError.constructor === Object) {
    fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/${name}`, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reqBody),
    })
      .then((res) => {
        if (res.status !== 202) {
          return {
            status: 'fail',
            message: 'Something went wrong',
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
      })
      .catch((err) => {
        // log to fluentd
        console.log(err)
      })
  }
}

export const getMsBsAe = name => (dispatch, getState) => {
  const { error } = getState().sim.configurations
  // since data is autocalculated, there should be no input errors
  if (name === 'ms') {
    delete error.ms_temp
    delete error.ms_rate_param
  }
  if (name === 'bs') {
    delete error.bs_temp
  }
  if (name === 'ae') {
    delete error.ae1_temp
    delete error.ae3_temp
  }

  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/${name}`, {
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
          message: 'Something went wrong',
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
          type: UPDATE_CONFIG,
          payload: {
            ...res.data,
            error,
          },
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      console.log(err)
    })
}

export const setAutoCalculate = (name, value) => (dispatch) => {
  dispatch({
    type: UPDATE_CONFIG,
    payload: {
      [name]: value,
    },
  })
}

export const updateConfig = (name, value, valError) => (dispatch, getState) => {
  const { error } = getState().sim.configurations
  if (Object.keys(valError).length === 0 && valError.constructor === Object) {
    delete error[name]
  }

  // update config in redux store
  dispatch({
    type: UPDATE_CONFIG,
    payload: {
      error: {
        ...error,
        ...valError,
      },
      [name]: value,
    },
  })

  // only make API request when there is no error
  if (Object.keys(valError).length === 0 && valError.constructor === Object) {
    fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/update`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ [name]: value }),
    })
      .then((res) => {
        if (res.status !== 202) {
          return {
            status: 'fail',
            message: 'Something went wrong',
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
      })
      .catch((err) => {
        // log to fluentd
        console.log(err)
      })
  }
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

  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/update`, {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      grain_size: grain_size_ASTM,
      nucleation_start,
      nucleation_finish,
      cct_cooling_rate,
      start_temp,
    }),
  }).catch(err => console.log(err))
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/simulate`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((res) => {
      if (res.status !== 200) {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      return res.json()
    })
    .then((simRes) => {
      if (simRes.status === 'fail') {
        return {
          status: 'fail',
          message: 'Something went wrong',
        }
      }
      if (simRes.status === 'success') {
        dispatch({
          type: RUN_SIM,
          payload: simRes.data,
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      console.log(err)
    })
}

export const updateCCTIndex = idx => (dispatch) => {
  dispatch({
    type: UPDATE_CCT_INDEX,
    payload: idx,
  })
}

/**
 * Schema of simulation object passed as arg
 * {
 *  alloys: { alloyOption, parent, weld, mix },
 *  configurations: {...},
 *  results: { USER, CCT, TTT },
 * }
 * @param {Object} sim simulation object
 */
export const loadSim = sim => (dispatch) => {
  dispatch({
    type: LOAD_SIM,
    payload: sim,
  })
}

export const loadSimFromLink = token => dispatch => (
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/share/simulation/view/${token}`, {
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
          message: 'Something went wrong',
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
        const {
          alloy_store,
          configurations: {
            grain_size,
            ...otherConfigs
          },
          simulation_results,
        } = res.data
        dispatch({
          type: LOAD_SIM,
          payload: {
            alloys: {
              alloyOption: alloy_store.alloy_option,
              parent: alloy_store.alloys.parent,
              weld: {
                _id: '',
                name: '',
                compositions: [],
              },
              mix: [],
            },
            configurations: {
              grain_size_ASTM: grain_size,
              grain_size_diameter: ASTM2Dia(grain_size),
              ...otherConfigs,
            },
            results: simulation_results,
          },
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      console.log(err)
    })
)

export const loadSimFromAccount = ({
  alloy_store, configurations, simulation_results,
}) => (dispatch) => {
  const { is_valid, grain_size, ...otherConfig } = configurations
  dispatch({
    type: LOAD_SIM,
    payload: {
      alloys: {
        alloyOption: alloy_store.alloy_option,
        parent: alloy_store.alloys.parent,
        weld: {
          _id: '',
          name: '',
          compositions: [],
        },
        mix: [],
      },
      configurations: {
        grain_size_ASTM: grain_size,
        ...otherConfig,
      },
      results: simulation_results,
    },
  })
}

export const loadPersistedSim = () => (dispatch, getState) => {
  const { lastSim } = getState().persist
  dispatch({
    type: LOAD_PERSISTED_SIM,
    payload: lastSim,
  })
}
