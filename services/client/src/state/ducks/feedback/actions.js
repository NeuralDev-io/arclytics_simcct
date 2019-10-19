import {
  UPDATE_FEEDBACK,
  CLOSE_FEEDBACK,
  RESET_FEEDBACK,
} from './types'
import { SIMCCT_URL } from '../../../constants'
import { addFlashToast } from '../toast/actions'
import { logError } from '../../../api/LoggingHelper'

/**
 * Update feedback in the Redux state. The reducer will take the
 * feedback parameters and spread it into the Redux state's feedback.
 * @param {any} feedback feedback object
 */
export const updateFeedback = feedback => (dispatch) => {
  dispatch({
    type: UPDATE_FEEDBACK,
    payload: feedback,
  })
}

/**
 * Close all feedback modals and set 'gotFeedback' in localStorage
 * to true so the app stop asking users for feedback.
 */
export const closeFeedback = () => (dispatch) => {
  dispatch({
    type: CLOSE_FEEDBACK,
  })
}

/**
 * Reset feedback Redux state to initial state.
 */
export const resetFeedback = () => (dispatch) => {
  dispatch({ type: RESET_FEEDBACK })
}

/**
 * Submit feedback to the API with data taken from the current Redux state.
 * If the request is successful, close the feedback modal, reset feedback state,
 * and create a success thank-you flash toast.
 */
export const submitFeedback = () => (dispatch, getState) => {
  const { category, rate, message } = getState().feedback
  fetch(`${SIMCCT_URL}/user/feedback`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      category,
      rating: rate,
      comment: message,
    }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        // close modal and reset state
        dispatch({ type: CLOSE_FEEDBACK })
        setTimeout(() => dispatch({ type: RESET_FEEDBACK }), 500)
        // dispatch success thank-you flash toast
        addFlashToast({
          message: 'Thank you for your feedback.',
          options: { variant: 'success' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'feedback.actions.submitFeedback', err.stack)
    })
}

/**
 * Submit a rating to the API
 * @param {number} rate Rating submitted by user
 */
export const submitRating = rate => (dispatch) => {
  fetch(`${SIMCCT_URL}/user/rating`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      rating: rate,
    }),
  })
    .then((res) => {
      if (res.status !== 200) {
        return {
          status: 'fail',
          message: 'Something went wrong',
        }
      }
      return res.json()
    })
    .then((res) => {
      if (res.status === 'fail') {
        addFlashToast({
          message: res.message,
          options: { variant: 'error' },
        }, true)(dispatch)
      }
      if (res.status === 'success') {
        // close modal and reset feedback state
        dispatch({ type: CLOSE_FEEDBACK })
        setTimeout(() => dispatch({ type: RESET_FEEDBACK }), 500)
        // dispatch success flash toast
        addFlashToast({
          message: 'Thank you for your feedback.',
          options: { variant: 'success' },
        }, true)(dispatch)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'feedback.actions.submitRating', err.stack)
    })
}
