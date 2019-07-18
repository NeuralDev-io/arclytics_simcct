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
 * TODO: in the future consider calling these functions on onBlur
 *
 * @version 1.0.0
 * @author Dalton Le
 */

export const updateComp = (type, alloy) => {
  fetch('http://localhost:8001/configs/comp/update', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_type: type,
      alloy,
    }),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
      if (data.status === 'success') console.log(data)
    })
}

export const updateConfig = () => {

}
