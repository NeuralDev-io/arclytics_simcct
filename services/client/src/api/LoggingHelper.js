/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Provides an the HTTP request fetch methods to for logging to the EFK stack.
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */

import { LOGGER_URL } from '../constants'

/**
 * Asynchronous fetch call which runs in a for-loop to attempt to try it
 * three times. If it fails after three attempts, we just ignore it and
 * return.
 *
 * @param {string} url - the url to send the fetch request to.
 * @param {object} options - the request body and any headers to send.
 * @param {number} n - the number of retry attempts.
 * @return {Promise<*|null>}
 */
const fetch_retry = async (url, options, n) => {
  // Because well, recursion is lame and for rookies.
  for (let i = 0; i < n; i += 1) {
    try {
      // eslint-disable-next-line no-await-in-loop
      return await fetch(url, options)
      // eslint-disable-next-line no-empty
    } catch (err) {}
  }
  return null
}

/**
 * This function uses the `in_http` plugin for `fluentd` to send a log to the
 * fluentd-logging` central logging layer. The logs are then forwarded to
 * `elasticsearch` data store which can then be viewed in `kibana`. Currently,
 * the host address is proxy passed from the nginx server for this `client`
 * microservice which is then forwarded to the `fluentd-logging` service layer.
 * The nginx server rewrites the URL to make the `tag.label` as the first
 * parameter after the matching parameter of `/logger` so that the logs are
 * correctly tagged.
 *
 * This arrow function also uses the `fetch_retry` method to try at least 3
 * times to log the message. It then ignores any errors or responses.
 *
 * Usage: URL --> https://host:port/tag.label
 *  - A `tag` is always `client`.
 *  - A `label` is one of either ["debug", "info", "error"] which matches the
 *   severity level of the log.
 * Body example:
 * {
 *   "log": string,
 *   "message": string,
 *   "source": string,
 *   "timestamp": ISO8016 date,
 *   "stack_trace": string,
 *   "caller": string (passed in from function),
 *   "severity": string (toUpperCase())
 * }
 *
 * @param log_message {string} as formatted message to log.
 * @param message {string} the actual message to log.
 * @param label {string} the label of the log.
 * @param caller {string} a passed in parameter for the calling function.
 * @param stack_trace {string} if catching exceptions, the stack trace.
 * @returns {Promise<*|null>}
 */
export const log = async (log_message, message, label, caller, stack_trace) => {
  const timestamp = new Date()
  return fetch_retry(
    `${LOGGER_URL}/client.${label}`, {
      method: 'POST',
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
  /**
   * Shortcut helper method provided to log `message` at the severity/label of `debug`.
   *
   * There is no return in all cases as the promise is ignored.
   *
   * @param {string} message - the log message to send.
   * @param {string} caller - the calling function to be passed in manually.
   */
  const label = 'debug'
  log(message, message, label, caller, '').then(() => {})
}

export const logInfo = (message, caller) => {
  /**
   * Shortcut helper method provided to log `message` at the severity/label of `info`.
   *
   * There is no return in all cases as the promise is ignored.
   *
   * @param {string} message - the log message to send.
   * @param {string} caller - the calling function to be passed in manually.
   */
  const label = 'info'
  log(message, message, label, caller, '').then(() => {})
}

export const logError = (log_message, message, caller, stack_trace) => {
  /**
   * Shortcut helper method provided to log `message` at the severity/label of `error`.
   *
   * There is no return in all cases as the promise is ignored.
   *
   * @param {string} message - the log message to send.
   * @param {string} caller - the calling function to be passed in manually.
   */
  const label = 'error'
  log(log_message, message, label, caller, stack_trace).then(() => {})
}
