/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * @version 0.1.0
 * @author Dalton Le
 *
 * This file provides helper asynchronous methods for update or reset
 * a Redis sim session
 */

import { SIMCCT_URL } from '../../constants'

/**
 * Dump the sim configs all at once to Redis session
 * @param {any} sim { alloy_store, configration } sim object
 */
export const updateSession = (sim) => (
  fetch(`${SIMCCT_URL}/session/update`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(sim),
  })
    .then(res => {
      if (res.status !== 200) throw new Error('Could not load simulation.')
      return res.json()
    })
)

export const resetSession = () => {

}
