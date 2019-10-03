/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides an the HTTP request fetch methods to support login and logout
 * processes to the API server.
 *
 * @version 0.9.0
 * @author Arvy Salazar, Andrew Che, Dalton Le
 *
 */

import { SIMCCT_URL } from '../constants'
import { logError } from './LoggingHelper'

export const login = async (values, resolve, reject) => {
  fetch(`${SIMCCT_URL}/auth/login`, {
    method: 'POST',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })
    .then((res) => {
      if (res.status === 200) {
        resolve(res.json())
      } else if (res.status === 404 || res.status === 403) {
      // return an error message as string
        res.json().then(object => reject(object.message))
      }
    })
    .catch((err) => logError(
      err.toString(), err.message, 'AuthenticationHelper.login', err.stack,
    ))
}

export const signup = async (values, resolve, reject) => {
  const {
    email, password, firstName, lastName,
  } = values
  fetch(`${SIMCCT_URL}/auth/register`, {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
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
    .catch((err) => logError(
      err.toString(), err.message, 'AuthenticationHelper.signup', err.stack,
    ))
}

export const logout = () => fetch(`${SIMCCT_URL}/auth/logout`, {
  method: 'GET',
  mode: 'cors',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
})
  .then(res => res.json())

/**
 * Check authentication status of current user.
 * This function will always return a resolved promise with
 * the state being the authentication status.
 *
 * Use it like this
 * checkAuthStatus()
 *  .then((res) => {
 *    if (res.status === 'success') { // do something }
 *    else { // do something }
 *  })
 */
export const checkAuthStatus = async () => {
  let auth
  try {
    auth = await fetch(`${SIMCCT_URL}/auth/status`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((res) => {
        if (res.status !== 200) {
          throw new Error('Unauthorised')
        }
        return res.json()
      })
      .then(res => res)
  } catch (err) {
    return { status: 'fail' }
  }
  return auth
}

export const checkPassword = async (password) => {
  let isPasswordValid = false
  try {
    isPasswordValid = await fetch(`${SIMCCT_URL}/auth/password/check`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password }),
    })
      .then((res) => {
        if (res.status !== 200) {
          throw new Error('Unauthorised')
        }
        return true
      })
  } catch (err) {
    isPasswordValid = false
  }
  return isPasswordValid
}

export const forgotPassword = (resolve, reject, email) => {
  fetch(`${SIMCCT_URL}/reset/password`, {
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
    .catch((err) => logError(
      err.toString(), err.message, 'AuthenticationHelper.forgotPassword', err.stack,
    ))
}

export const resetPassword = (resolve, reject, values, token) => {
  fetch(`${SIMCCT_URL}/auth/password/reset`, {
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
        resolve(res)
      } else {
        reject(res.message)
      }
    })
    .catch((err) => logError(
      err.toString(), err.message, 'AuthenticationHelper.reset', err.stack,
    ))
}

export const resendVerify = (resolve, reject, email) => {
  fetch(`${SIMCCT_URL}/confirm/register/resend`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
    })
  })
    .then(res => res.json())
    .then((res) => {
        if (res.status === 'success'){
          resolve(res.message)
        } else {
          reject(res)
        }
      }
    )
    .catch(err => {
      console.log(err)
    })
}
