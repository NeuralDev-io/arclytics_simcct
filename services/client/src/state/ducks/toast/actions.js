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

/**
 * Remove a flash toast from Redux store.
 * This is called after Toaster has displayed the toast.
 * @param {string} key key of the flash toast
 */
export const removeFlashToast = key => (dispatch) => {
  dispatch({
    type: REMOVE_FLASH_TOAST,
    key,
  })
}
