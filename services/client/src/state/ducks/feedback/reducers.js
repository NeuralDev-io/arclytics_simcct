import {
  UPDATE_FEEDBACK,
  CLOSE_FEEDBACK,
  RESET_FEEDBACK,
} from './types'

const initialState = {
  visible: false,
  backdrop: false,
  givingFeedback: false,
  rate: -1,
  message: '',
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_FEEDBACK:
      return {
        ...state,
        ...action.payload,
      }
    case CLOSE_FEEDBACK:
      return {
        ...state,
        visible: false,
        backdrop: false,
      }
    case RESET_FEEDBACK:
      return {
        ...initialState,
      }
    default:
      return state
  }
}

export default reducer
