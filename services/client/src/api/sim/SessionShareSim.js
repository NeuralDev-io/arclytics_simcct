/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * @version 0.1.0
 * @author Andrew Che
 */

// TODO(andrew@neuraldev.io): Do documentation.
export const getShareUrlLink = (configs, alloyStore, results) => new Promise((resolve, reject) => {
  /**
   * API request method to get the sharing URL link from the `users` server.
   *
   * The successful response will be:
   * {
   *   "status": "success",
   *   "link": "..."
   * }
   * */
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/share/simulation/link`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      configurations: configs,
      alloy_store: alloyStore,
      simulation_results: results,
    }),
  })
    .then(res => res.json())
    .then((resp) => {
      if (resp.status === 'fail') throw new Error(resp.message)
      if (resp.status === 'success') resolve(resp)
    })
    .catch(err => reject(err))
})

export const sendShareEmail = (emails, message, configurations, alloyStore, results) => new Promise(
  (resolve, reject) => {
    /**
     * API request method to get the sharing URL link from the `users` server.
     *
     * The successful response will be:
     * {
     *   "status": "success",
     *   "message": "Email(s) sent.",
     *   "link": "..."
     * }
     * */
    fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/share/simulation/email`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        alloy_store: alloyStore,
        emails,
        message,
        configurations,
        simulation_results: results,
      }),
    })
      .then(res => res.json())
      .then((resp) => {
        if (resp.status === 'fail') throw new Error(resp.message)
        if (resp.status === 'success') resolve(resp)
      })
      .catch(err => reject(err))
  },
)
