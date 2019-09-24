import { PERSIST_SIM } from './types'

// eslint-disable-next-line import/prefer-default-export
export const persistSim = () => (dispatch, getState) => {
  const { sim } = getState()
  dispatch({
    type: PERSIST_SIM,
    payload: sim,
    time: new Date().toISOString(),
  })
}
