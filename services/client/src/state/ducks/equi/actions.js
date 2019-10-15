/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Actions used to make API requests to the and `simcct` microservice to
 * get the equilibrium values and plot
 *
 *
 * @version 1.0.0
 * @author Dalton Le
 */


import { GET_EQUI_VALUES } from './types'
import { addFlashToast } from '../toast/actions'
import { SIMCCT_URL } from '../../../constants'
import { logError } from '../../../api/LoggingHelper'

/**
 * Get the equilibrium values and plot from the simcct microservice via
 * a POST request, request body contains the alloy store and ae1 temp pulled
 * straight from Redux store.
 * If successful, response will have body
 * {
 *    status: 'success',
 *    data: {
 *      ferrite_phase_frac: number,
        eutectic_composition_carbon: number,
        cf: number,
        results_plot: {},
 *    }
 * }
 */
// eslint-disable-next-line
export const getEquilibriumValues = () => (dispatch, getState) => {
  const { alloys, configurations: { ae1_temp } } = getState().sim
  dispatch({
    type: GET_EQUI_VALUES,
    status: 'started',
  })

  fetch(`${SIMCCT_URL}//alloys`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      alloy_store: {
        alloy_option: alloys.alloyOption,
        parent: alloys.parent,
      },
      ae1_temp,
    }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Counld\'t generate equilibrium plot',
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
        dispatch({
          type: GET_EQUI_VALUES,
          status: 'fail',
        })
      }
      if (res.status === 'success') {
        dispatch({
          type: GET_EQUI_VALUES,
          status: 'success',
          payload: {
            xfe: res.data.ferrite_phase_frac,
            ceut: res.data.eutectic_composition_carbon,
            cf: res.data.cf,
            plot: res.data.results_plot,
          },
        })
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'equi.actions.getEquilibriumValues', err.stack)
    })
}
