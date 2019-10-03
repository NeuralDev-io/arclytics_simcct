import {
  ADD_SIM,
  GO_FORWARD,
  GO_BACKWARD,
  GO_TO_POINT,
} from './types'
import {
  LOAD_SIM,
} from '../sim/types'

export const addSimToTimeMachine = () => (dispatch, getState) => {
  const { sim } = getState()
  dispatch({
    type: ADD_SIM,
    payload: sim,
    timestamp: new Date().toISOString(),
  })
}

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
