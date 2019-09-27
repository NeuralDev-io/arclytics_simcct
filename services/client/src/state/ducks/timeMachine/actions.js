import {
  ADD_SIM,
  REMOVE_SIM,
  GO_FORWARD,
  GO_BACKWARD,
} from './types'

export const addSimToTimeMachine = sim => (dispatch, getState) => {
  const { capacity, data } = getState().timeMachine
  // check if capacity is maxed then remove one oldest sim
  if (data.length === capacity) {
    dispatch({ type: REMOVE_SIM })
  }
  dispatch({
    type: ADD_SIM,
    payload: sim,
  })
}

export const timeTravelBack = () => (dispatch, getState) => {
  const { data, current } = getState().timeMachine
  // load sim to app


  // set back current position by 1
  dispatch({ type: GO_BACKWARD })
}

export const timeTravelNext = () => (dispatch, getState) => {
  const { data, current } = getState().timeMachine
  // load sim to app


  // set back current position by 1
  dispatch({ type: GO_FORWARD })
}
