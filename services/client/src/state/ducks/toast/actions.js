import {
  ADD_FLASH_TOAST,
  REMOVE_FLASH_TOAST,
} from './types'

/**
 * Add a notification to Redux store
 * @param {object} notification Notification object {message, options}
 * @param {boolean} dismissable (optional) Pass in true if you want to add a Dismiss button
 */
export const addFlashToast = (notification, dismissable = false) => (dispatch) => {
  dispatch({
    type: ADD_FLASH_TOAST,
    notification: {
      key: new Date().getTime() + Math.random(),
      dismissable,
      ...notification,
    },
  })
}

export const removeFlashToast = key => (dispatch) => {
  dispatch({
    type: REMOVE_FLASH_TOAST,
    key,
  })
}
