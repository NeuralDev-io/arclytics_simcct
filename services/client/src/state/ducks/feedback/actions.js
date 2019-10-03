import {
  UPDATE_FEEDBACK,
  CLOSE_FEEDBACK,
  RESET_FEEDBACK,
} from './types'
import { SIMCCT_URL } from '../../../constants'
import { addFlashToast } from '../toast/actions'
import { logError } from '../../../api/LoggingHelper'

export const updateFeedback = feedback => (dispatch) => {
  dispatch({
    type: UPDATE_FEEDBACK,
    payload: feedback,
  })
}

export const closeFeedback = () => (dispatch) => {
  dispatch({
    type: CLOSE_FEEDBACK,
  })
  localStorage.setItem('gotFeedback', true)
}

export const resetFeedback = () => (dispatch) => {
  dispatch({ type: RESET_FEEDBACK })
}

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
        dispatch({ type: CLOSE_FEEDBACK })
        setTimeout(() => dispatch({ type: RESET_FEEDBACK }), 500)
        addFlashToast({
          message: 'Thank you for your feedback.',
          options: { variant: 'success' },
        }, true)(dispatch)
        localStorage.setItem('gotFeedback', true)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'feedback.actions.submitFeedback', err.stack)
    })
}

export const submitRating = rate => (dispatch, getState) => {
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
        dispatch({ type: CLOSE_FEEDBACK })
        setTimeout(() => dispatch({ type: RESET_FEEDBACK }), 500)
        addFlashToast({
          message: 'Thank you for your feedback.',
          options: { variant: 'success' },
        }, true)(dispatch)
        localStorage.setItem('gotFeedback', true)
      }
    })
    .catch((err) => {
      // log to fluentd
      logError(err.toString(), err.message, 'feedback.actions.submitRating', err.stack)
    })
}
