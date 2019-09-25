import {
  UPDATE_FEEDBACK,
  CLOSE_FEEDBACK,
  RESET_FEEDBACK,
} from './types'
import { addFlashToast } from '../toast/actions'

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
}

export const resetFeedback = () => (dispatch) => {
  dispatch({ type: RESET_FEEDBACK })
}

export const submitFeedback = () => (dispatch, getState) => {
  const { category, rate, message } = getState().feedback
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/feedback`, {
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
      console.log(err)
    })
}

export const submitRating = rate => (dispatch, getState) => {
  fetch(`${process.env.REACT_APP_SIM_HOST}:${process.env.REACT_APP_SIM_PORT}/api/v1/sim/user/rating`, {
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
      console.log(err)
    })
}