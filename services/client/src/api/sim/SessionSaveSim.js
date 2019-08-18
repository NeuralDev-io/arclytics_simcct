/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Functions used to update the current session configurations, used in the main
 * simulation screen. These functions are called each time onChange is fired on an
 * config/comp input field. The purpose is to speed up the time it takes since a
 * user presses RUN until the result is returned.
 *
 *
 * @version 0.1.0
 * @author Andrew Che
 */

// TODO(andrew@neuraldev.io): Find out why trying to get env from Docker no work
// const usersServer = process.env.USERS_HOST

export const postSaveSimulation = (configs, alloyStore) => {
  /**
   * API call to `users` server to save a new saved simulation for the user.
   * User's are identified by the JWT token passed as an Authorization header.
   * @param {configs} a configurations object.
   * @param {alloyStore} an alloy store object which contains an `alloy_option`,
   * and a nested `alloys` object with `parent`, `weld`, or `mix` alloy objects.
   */
  fetch('http://localhost:8000/user/simulation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      configurations: configs,
      alloy_store: alloyStore,
    }),
  }).then(res => res.json())
    .then((data) => {
      // TODO(andrew@neuraldev.io): Not complete. Not really sure what to do
      //  with a successful save. I would like to have a message pop-up somewhere
      //  but it seems there are no flash messaging components yet.
      // eslint-disable-next-line no-console
      console.log(data)
    })
    // eslint-disable-next-line no-console
    .catch(err => console.log(err))
}

// TODO(andrew@neuraldev.io): Fix this to dispatch the data back to component
export const getSavedSimulationList = () => {
  /**
   * API call to `users` server to retrieve the user's list of saved simulations.
   * Returns a list of saved simulations as an `application/json` content-type
   * with the following schema:
   *
   * {
   *    "status": "success",
   *    "data": [
   *      {"_id": "ObjectId", "configurations": {...}, "alloy_store": {...}},
   *      {...},
   *      {...}
   *    ]
   * }
   */
  fetch('http://localhost:8000/user/simulation', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  }).then(res => res.json())
    .then((data) => {
      // eslint-disable-next-line no-console
      console.log(data)
    })
    // eslint-disable-next-line no-console
    .catch(err => console.log(err))
}

// TODO(andrew@neuraldev.io): Add the GET detail API function.
