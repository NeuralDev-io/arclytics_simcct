import {
  ADD_SIM,
  GO_FORWARD,
  GO_BACKWARD,
  GO_TO_POINT,
} from './types'
import {
  LOAD_SIM,
} from '../sim/types'

/**
 * Add the current simulation to the time machine's history, along with
 * the current timestamp
 */
export const addSimToTimeMachine = () => (dispatch, getState) => {
  const { sim } = getState()
  dispatch({
    type: ADD_SIM,
    payload: sim,
    timestamp: new Date().toISOString(),
  })
}

/**
 * Go back to the last simulation saved in history.
 * Load this simulation into the app and move the current cursor
 * back by 1
 */
export const timeTravelBack = () => (dispatch, getState) => {
  const { data, current } = getState().timeMachine
  // load sim to app
  const { sim } = data[current - 1]
  dispatch({
    type: LOAD_SIM,
    payload: sim,
  })

  // set back current position by 1
  dispatch({ type: GO_BACKWARD })
}

/**
 * Go back to the next simulation saved in history.
 * Load this simulation into the app and move the current cursor
 * forward by 1
 */
export const timeTravelNext = () => (dispatch, getState) => {
  const { data, current } = getState().timeMachine
  // load sim to app
  const { sim } = data[current + 1]
  dispatch({
    type: LOAD_SIM,
    payload: sim,
  })

  // set back current position by 1
  dispatch({ type: GO_FORWARD })
}

/**
 * Go to a certain simulation saved in history.
 * Load this simulation into the app and move the current cursor
 * to this position.
 * @param {number} index index of the simulation
 */
export const timeTravelTo = index => (dispatch, getState) => {
  const { data } = getState().timeMachine
  // load sim to app
  const { sim } = data[index]
  dispatch({
    type: LOAD_SIM,
    payload: sim,
  })

  // set current position
  dispatch({ type: GO_TO_POINT, payload: index })
}
