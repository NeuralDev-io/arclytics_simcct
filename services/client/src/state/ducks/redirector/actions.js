/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Actions used to make manage the redirector state.
 * The redirector state is used to navigate outside of the component tree.
 * A Redirector component will watch for any location object that is added
 * to the redirector state and navigate to that location.
 *
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import { ADD_LOCATION, REMOVE_LOCATION } from './types'

/**
 * Add a new location to the redirector state
 * The location will have the schema
 * {
 *    pathname: string,
 *    search: string,
 *    state: {},
 * }
 * Only `pathname` is required.
 *
 * @param {object} notification Notification object {message, options}
 * @param {boolean} dismissable (optional) Pass in true if you want to add a Dismiss button
 */
export const addLocation = location => (dispatch) => {
  dispatch({
    type: ADD_LOCATION,
    payload: {
      key: new Date().getTime() + Math.random(),
      location,
    },
  })
}

/**
 * Remove a location to the redirector state.
 * This is called after Redirector has navigated the app to said location.
 * @param {string} key key of the flash toast
 */
export const removeLocation = key => (dispatch) => {
  dispatch({
    type: REMOVE_LOCATION,
    payload: key,
  })
}
