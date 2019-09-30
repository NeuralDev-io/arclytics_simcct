/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides an the HTTP request fetch methods to for logging to the EFK stack.
 *
 * @version 0.0.1
 * @author Andrew Che
 *
 */

import { LOGGER_URL } from '../constants'

/*
* TODO(andrew@neuraldev.io):
*  - Make a log function for different levels.
*  - Retry the logger at least 3 times before ignoring it.
*  - Find a way to get the timestamp.
*  - Make the Arclytics backend to accept these log calls.
* */

/*
* This method uses the fluent package plugin called in_http which exposes
* an endpoint that will accept a log from the http source such as this
* fetch request.
*
* Usage: URL --> https://host:port/tag.label
* Body: {"container_name": string, "log": string, "source": string}
* */
// eslint-disable-next-line import/prefer-default-export
export const log = async (message, label, caller) => fetch(
  // Try to make the log call once and if it fails, return the failed response.
  `${LOGGER_URL}/client.${label}`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      // tag: `${tag}.${label}`,
      log: message,
      source: 'http',
      timestamp: Date.now(),
      severity: label.toUpperCase(),
      caller,
      message,
    }),
  //  Ignore both the response and any errors
  },
).then((res) => {
  if (res.status !== 200) return { status: 'failed' }
  return { status: 'succeeded' }
})

// TODO(andrew@neuraldev.io): Meh, find a better way to do recursion.
export const logDebug = (message, caller) => {
  const label = 'debug'
  log(message, label, caller).then((res) => {
    if (res.status === ' failed') {
      log(message, label, caller).then((res2) => {
        if (res2.status === ' failed') log(message, label, caller).then(() => {})
      })
    }
  })
}

// TODO(andrew@neuraldev.io): Meh, find a better way to do recursion.
export const logInfo = (message, caller) => {
  const label = 'info'
  log(message, label, caller).then((res) => {
    if (res.status === ' failed') {
      log(message, label, caller).then((res2) => {
        if (res2.status === ' failed') log(message, label, caller).then(() => {})
      })
    }
  })
}


// TODO(andrew@neuraldev.io): Meh, find a better way to do recursion.
export const logError = (message, caller) => {
  const label = 'error'
  log(message, label, caller).then((res) => {
    if (res.status === ' failed') {
      log(message, label, caller).then((res2) => {
        if (res2.status === ' failed') log(message, label, caller).then(() => {})
      })
    }
  })
}
