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
*  - Documentation
* - DONE -- Make a log function for different levels.
* - DONE -- Retry the logger at least 3 times before ignoring it.
* - DONE -- Find a way to get the timestamp.
* */


const fetch_retry = async (url, options, n) => {
  // Because well, recursion is lame and for rookies.
  for (let i = 0; i < n; i += 1) {
    try {
      // eslint-disable-next-line no-await-in-loop
      return await fetch(url, options)
    } catch (err) {
      const isLastAttempt = i + 1 === n
      if (isLastAttempt) throw err
    }
  }
  return null
}

/*
*
*
* Usage: URL --> https://host:port/tag.label
* Body: {"container_name": string, "log": string, "source": string}
* */
export const log = async (log_message, message, label, caller, stack_trace) => {
  const timestamp = new Date()
  return fetch_retry(
    `${LOGGER_URL}/client.${label}`, {
      method: 'POST',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        log: log_message,
        source: 'http',
        timestamp: timestamp.toISOString(),
        severity: label.toUpperCase(),
        stack_trace,
        caller,
        message,
      }),
    },
    3,
  )
}

export const logDebug = (message, caller) => {
  const label = 'debug'
  log(message, message, label, caller, '').then(() => {})
}

export const logInfo = (message, caller) => {
  const label = 'info'
  log(message, message, label, caller, '').then(() => {})
}

export const logException = (log_message, message, caller, stack_trace) => {
  const label = 'error'
  log(log_message, message, label, caller, stack_trace).then(() => {})
}


export const logError = (log_message, message, caller, stack_trace) => {
  const label = 'error'
  log(log_message, message, label, caller, stack_trace).then(() => {})
}
