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
  LOAD_LAST_SIM,
  LOAD_SIM_FROM_FILE,
  RESET_SIM,
} from './types'
import { SIMCCT_URL } from '../../../constants'
import { ASTM2Dia } from '../../../utils/grainSizeConverter'
import { addFlashToast } from '../toast/actions'
import { addSimToTimeMachine } from '../timeMachine/actions'
import { logError } from '../../../api/LoggingHelper'

export const resetSession = () => (dispatch) => {
  // make api call to update session
  dispatch({
    type: RESET_SIM,
  })
}

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
  fetch(`${SIMCCT_URL}/alloys/update`, {
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
      logError(err.toString(), err.message, 'actions.initSession', err.stack)
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
 * @param {string} error
 * @param {object} alloy alloy to be updated
 */
export const updateComp = (option, type, alloy, error) => (dispatch) => {
  dispatch({
    type: UPDATE_COMP,
    config: {},
    alloyType: type,
    alloy,
    parentError: error,
  })

  // only make API request if error free
  if (Object.keys(error).length === 0) {
    fetch(`${SIMCCT_URL}/alloys/update`, {
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
      })
      .catch((err) => {
        logError(err.toString(), err.message, 'actions.updateComp', err.stack)
      })
  }
}

/**
 * [DEPRECATED]
 *
 * Update the dilution value and calculate the new mix composition.
 * NOTE: This function is incomplete but it's fine because the feature
 * is no longer requried by the client.
 *
 * @param {number} val dilution value
 */
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
  fetch(`${SIMCCT_URL}/configs/method/update`, {
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
      logError(err.toString(), err.message, 'actions.updateConfigMethod', err.stack)
    })
}

/**
 * Update grain size in the Redux store.
 * Only make API request to update Redis session when there are no errors.
 *
 * @param {string|number} astm ASTM grain size
 * @param {string|number} dia grain size in diameter
 * @param {any} grainSizeError error object
 */
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
    fetch(`${SIMCCT_URL}/configs/update`, {
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
        logError(err.toString(), err.message, 'actions.updateGrainSize', err.stack)
      })
  }
}

/**
 * Update the transformation limits. Only make API request to
 * update Redis session if there are no errors.
 * @param {string} name name of the phase - 'ms' | 'bs' | 'ae'
 * @param {string} field field to be updated
 * @param {any} data config object
 * @param {any} valError error object
 */
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
    fetch(`${SIMCCT_URL}/configs/${name}`, {
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
        logError(err.toString(), err.message, 'actions.updateMsBsAe', err.stack)
      })
  }
}

/**
 * Get the autocalculated transformation limits.
 * @param {string} name name of the phase - 'ms' | 'bs' | 'ae'
 */
export const getMsBsAe = name => (dispatch, getState) => {
  const { error } = getState().sim.configurations
  // since data is autocalculated, there should be no input errors
  // delete all input errors from these fields
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

  fetch(`${SIMCCT_URL}/configs/${name}`, {
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
      logError(err.toString(), err.message, 'actions.getMsBsAe', err.stack)
    })
}

/**
 * Set auto-calculate of tranformation limits in the Redux state.
 * @param {string} name name of the phase - 'ms' | 'bs' | 'ae'
 * @param {boolean} value new value of auto-calculate
 */
export const setAutoCalculate = (name, value) => (dispatch) => {
  dispatch({
    type: UPDATE_CONFIG,
    payload: {
      [name]: value,
    },
  })
}

/**
 * Update config in Redux state, only submit API requests if there are no errors.
 * @param {string} name name of config field to be updated
 * @param {string|number} value new value
 * @param {any} valError object error
 */
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
    fetch(`${SIMCCT_URL}/configs/update`, {
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
        logError(err.toString(), err.message, 'actions.updateConfig', err.stack)
      })
  }
}

/**
 * Update whether or not to display user cooling curve
 * @param {boolean} value whether to display user curve or not
 */
export const toggleDisplayUserCurve = value => (dispatch) => {
  dispatch({
    type: UPDATE_DISPLAY_USER_CURVE,
    payload: value,
  })
}

/**
 * Get the simulation results of the current sim session
 */
export const runSim = () => (dispatch, getState) => {
  const {
    grain_size_ASTM,
    nucleation_start,
    nucleation_finish,
    cct_cooling_rate,
    start_temp,
  } = getState().sim.configurations

  fetch(`${SIMCCT_URL}/configs/update`, {
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
  }).catch(err => logError(err.toString(), err.message, 'actions.runSim', err.stack))
  fetch(`${SIMCCT_URL}/simulate`, {
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
        addSimToTimeMachine()(dispatch, getState)
        // update sim count in localStorage
        const currentSimCount = localStorage.getItem('simCount')
        if (currentSimCount === undefined) {
          localStorage.setItem('simCount', 1)
        } else {
          let simCount
          try {
            simCount = parseFloat(currentSimCount) + 1
          } catch (err) {
            // do nothing
          }
          if (Number.isNaN(simCount)) {
            simCount = 1
          }
          localStorage.setItem('simCount', simCount)
          localStorage.setItem('gotFeedback', false)
        }
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'actions.runSim', err.stack)
    })
}

/**
 * Update CCTIndex in Redux store
 * @param {number} idx new index for the user curve data array
 */
export const updateCCTIndex = idx => (dispatch) => {
  dispatch({
    type: UPDATE_CCT_INDEX,
    payload: idx,
  })
}

/**
 * Load a sim into the app
 * @param {any} sim simulation object
 */
export const loadSim = sim => (dispatch) => {
  dispatch({
    type: LOAD_SIM,
    payload: sim,
  })
}

/**
 * Schema of simulation object passed as arg
 * {
 *  alloys: { alloyOption, parent, weld, mix },
 *  configurations: {...},
 *  results: { USER, CCT, TTT },
 * }
 * @param {any} sim simulation object
 */
export const loadSimFromFile = sim => (dispatch) => {
  dispatch({
    type: LOAD_SIM_FROM_FILE,
    payload: sim,
  })
}

/**
 * Request a shared simulation by using token and load it
 * into the app
 * @param {string} token token to access sim link
 */
export const loadSimFromLink = token => dispatch => (
  fetch(`${SIMCCT_URL}/user/share/simulation/view/${token}`, {
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
      logError(err.toString(), err.message, 'actions.loadSimFromLink', err.stack)
    })
)

/**
 * Load a saved simulation into the app
 * @param {any} param0 simulation object
 */
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
        grain_size_diameter: ASTM2Dia(parseFloat(grain_size)),
        ...otherConfig,
      },
      results: simulation_results,
    },
  })
}

/**
 * Load most recent simulation saved in localStorage into the app
 */
export const loadPersistedSim = () => (dispatch, getState) => {
  const { lastSim } = getState().persist
  dispatch({
    type: LOAD_PERSISTED_SIM,
    payload: lastSim,
  })
}

/**
 * Load the last simulation tied to an account into the app.
 * This will be called when a user logs back in after a period of time > 2 hours.
 */
export const loadLastSim = () => (dispatch, getState) => {
  const { lastSim } = getState().self
  const { last_configuration: { grain_size, is_valid, ...otherConfig } } = lastSim
  const convertedConfig = {
    ...otherConfig,
    grain_size_ASTM: grain_size,
    grain_size_diameter: ASTM2Dia(parseFloat(grain_size)),
  }
  dispatch({
    type: LOAD_LAST_SIM,
    payload: {
      ...lastSim,
      last_configuration: convertedConfig,
    },
  })
}
