import {
  UPDATE_FEEDBACK,
  CLOSE_FEEDBACK,
  RESET_FEEDBACK,
  GET_FEEDBACK,
} from './types'

const initialState = {
  feedbackList: {
    data: [],
    isFetched: false,
    isLoading: false,
    /*
    * TODO(andrew@neuraldev.io): add the required pagination state
    *  - sort, offset, limit, next_offset, prev_offset, n_results, current_page, total_pages
    * */
  },
  feedbackVisible: false,
  ratingVisible: false,
  backdrop: false,
  givingFeedback: false,
  category: '',
  rate: -1,
  message: '',
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_FEEDBACK: {
      if (action.status === 'started') {
        return {
          ...state,
          feedbackList: {
            ...state.feedbackList,
            isLoading: true,
          },
        }
      }

      // Let's deal with failure first so we can get over it faster (i.e. fail fast)
      if (action.status === 'fail') {
        return {
          ...state,
          feedbackList: {
            ...state.feedbackList,
            isLoading: false,
          },
        }
      }

      // If action.status === 'success'
      if (action.status === 'success') {
        return {
          ...state,
          feedbackList: {
            ...state.feedbackList,
            isLoading: false,
            isFetched: true,
            data: action.payload,
          },
        }
      }
      break
    }
    case UPDATE_FEEDBACK:
      return {
        ...state,
        ...action.payload,
      }
    case CLOSE_FEEDBACK:
      return {
        ...state,
        feedbackVisible: false,
        ratingVisible: false,
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
