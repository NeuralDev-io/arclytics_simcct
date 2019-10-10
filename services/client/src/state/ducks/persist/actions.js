import { PERSIST_SIM } from './types'

/**
 * Save the current Sim session to localStorage along with a timestamp.
 * Next time the user accesses the SimPage, this Sim session will be loaded
 * if the timestamp has not been passed by 2 hours.
 */
// eslint-disable-next-line import/prefer-default-export
export const persistSim = () => (dispatch, getState) => {
  const { sim } = getState()
  dispatch({
    type: PERSIST_SIM,
    payload: sim,
    time: new Date().toISOString(),
  })
}
