import { PERSIST_SIM, RESET } from './types'

export const persistSim = () => (dispatch, getState) => {
  const { sim } = getState()
  dispatch({
    type: PERSIST_SIM,
    payload: sim,
  })
}

export const resetPersist = () => (dispatch) => {
  dispatch({
    type: RESET,
  })
}
