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

/**
 * Add a location to navigate back to sign in page.
 * This action will be called when an API request receives 401 code response.
 *
 * This function initially add a FlashToast to notify the user that session
 * has expired. However this was moved to LoginPage to avoid the possibility
 * of multiple 401 API requests calling forceSignIn at the same time leading to
 * multiple toasts displayed.
 */
export const forceSignIn = (message = 'Your session has expired. Please sign in again.') => (dispatch) => {
  dispatch({
    type: ADD_LOCATION,
    payload: {
      key: new Date().getTime() + Math.random(),
      location: {
        pathname: '/signin',
        state: {
          forcedOut: true,
          forcedOutMessage: message,
        },
      },
    },
  })
  dispatch({ type: 'USER_LOGOUT' })
}
