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
 * @version 1.0.0
 * @author Dalton Le
 */

export const initComp = (option, type, alloy) => {
  fetch('http://localhost:8001/alloys/update', {
    method: 'POST',
    // credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy,
    }),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
    })
    .catch(err => console.log(err))
}

export const updateComp = (option, type, alloy) => {
  fetch('http://localhost:8001/alloys/update', {
    method: 'PATCH',
    // credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy,
    }),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
    })
    .catch(err => console.log(err))
}

export const updateConfigMethod = (value) => {
  fetch('http://localhost:8001/configs/method/update', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ method: value }),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
    })
    .catch(err => console.log(err))
}

export const updateConfig = (reqBody) => {
  fetch('http://localhost:8001/configs/update', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(reqBody),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
    })
    .catch(err => console.log(err))
}

export const updateMsBsAe = (name, reqBody) => {
  fetch(`http://localhost:8001/${name}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(reqBody),
  })
    .then(res => res.json())
    .then((data) => {
      if (data.status === 'fail') throw new Error(data.message)
    })
    .catch(err => console.log(err))
}

export const getMsBsAe = (name, callback) => {
  fetch(`http://localhost:8001/${name}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((data) => {
      const { status, ...others } = data
      if (status === 'fail') throw new Error(data.message)
      if (status === 'success') {
        // use callback function to set state to SimulationPage
        callback(prevState => ({
          configurations: {
            ...prevState.configurations,
            ...others,
          },
        }))
      }
    })
    .catch(err => console.log(err))
}
