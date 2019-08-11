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

const usersServer = process.env.USERS_HOST

// eslint-disable-next-line import/prefer-default-export
export const postSaveSimulation = () => {
  fetch('http://localhost:8000/user/simulation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      configurations: '',
      alloy_store: '',
    }),
  }).then(res => res.json())
    .then((data) => {
      // eslint-disable-next-line no-console
      if (data.status === 'fail') console.log(data)
    })
    // eslint-disable-next-line no-console
    .catch(err => console.log(err))
}
