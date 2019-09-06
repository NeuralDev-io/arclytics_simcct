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

export const initComp = (option, type, alloy) => new Promise((resolve, reject) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/alloys/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy,
    }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') resolve(res.data)
    })
    .catch(err => reject(err))
})

export const updateComp = (option, type, alloy) => new Promise((resolve, reject) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/alloys/update`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      alloy_option: option,
      alloy_type: type,
      alloy,
    }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') resolve(res.data)
    })
    .catch(err => reject(err))
})

export const updateConfigMethod = (value) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/method/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ method: value }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
    })
    .catch(err => console.log(err))
}

export const updateConfig = (reqBody) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/update`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(reqBody),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
    })
    .catch(err => console.log(err))
}

export const updateMsBsAe = (name, reqBody) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/${name}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(reqBody),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
    })
    .catch(err => console.log(err))
}

export const getMsBsAe = name => new Promise((resolve, reject) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/configs/${name}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'fail') throw new Error(res.message)
      if (res.status === 'success') resolve(res.data)
    })
    .catch(err => reject(err))
})
