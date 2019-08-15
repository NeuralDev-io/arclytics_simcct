/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * @version 0.1.0
 * @author Andrew Che
 */

// TODO(andrew@neuraldev.io): Do documentation.
export const getShareUrlLink = (configs, alloyStore) => new Promise((resolve, reject) => {
  fetch('http://localhost:8000/user/share/simulation/link', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      configurations: configs,
      alloy_store: alloyStore,
    }),
  })
    .then(res => res.json())
    .then((resp) => {
      if (resp.status === 'fail') throw new Error(resp.message)
      if (resp.status === 'success') resolve(resp)
    })
    .catch(err => reject(err))
})

export const sendShareEmail = (configs, alloyStore, resolve, reject) => {}
