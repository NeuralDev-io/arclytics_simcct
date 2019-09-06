/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides an the HTTP request fetch methods to support login and logout
 * processes to the API server.
 *
 * @version 0.9.0
 * @author Arvy Salazar, Andrew Che, Dalton Le
 * @github Xaraox
 */

const ARC_URL = `http://${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim`

export const login = async (values, resolve, reject) => {
  fetch(`${ARC_URL}/auth/login`, {
    method: 'POST',
    mode: 'cors',
    headers: {
      'content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status === 200) {
        resolve(res.json())
      } else if (res.status === 404) {
      // return an error message as string
        res.json().then(object => reject(object.message))
      }
    })
    .catch(err => console.log(err))
}


export const signup = async (values, resolve, reject) => {
  const {
    email, password, firstName, lastName,
  } = values
  fetch(`${ARC_URL}/auth/register`, {
    method: 'POST',
    mode: 'cors',
    headers: {
      'content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    }),
  })
    .then((res) => {
      if (res.status === 201) {
        resolve(res.json())
      } else if (res.status === 400) {
        // return an error message as string
        res.json().then(object => reject(object.message))
      }
    })
    .catch(err => console.log(err))
}

export const logout = (callback) => {
  fetch(`${ARC_URL}/auth/logout`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Session: localStorage.getItem('session'),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })
    .then(res => res.json())
    .then(() => {
      /*
      * TODO(andrew@neuraldev.io): Until you fix the backend logout if there is
      *  no persistent storage across Redis sessions, just let this one through.
      * */
      // if (data.status === 'fail') throw new Error(data.message)
      // if (data.status === 'success') {
      localStorage.removeItem('token')
      localStorage.removeItem('session')
      localStorage.removeItem('persist:userStatus')
      callback('/signin')
      // }
    })
    .catch(err => console.log(err))
}

export const forgotPassword = (resolve, reject, email) => {
  fetch(`${ARC_URL}/reset/password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
    }),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'success') {
        resolve(res.message)
      } else {
      // return an error message as string
        reject(res.message)
      }
    })
    .catch(err => console.log(err))
}

export const resetPassword = (resolve, reject, values, token) => {
  fetch(`${ARC_URL}/auth/password/reset`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(values),
  })
    .then(res => res.json())
    .then((res) => {
      if (res.status === 'success') {
        console.log(res.status, res.message)
        resolve(res)
      } else {
        console.log(res.status, res.message)
        reject(res.message)
      }
    })
    .catch(err => console.log(err))
}
