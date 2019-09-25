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
  const { rate, message } = getState().feedback
  console.log(rate, message)
  dispatch({ type: CLOSE_FEEDBACK })
  dispatch({ type: RESET_FEEDBACK })
}
