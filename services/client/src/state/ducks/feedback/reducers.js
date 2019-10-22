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
    sort: '-created_date',
    limit: 10,
    current_page: -1,
    total_pages: -1,
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
            data: action.payload.data,
            sort: action.payload.sort,
            limit: action.payload.limit,
            current_page: action.payload.current_page,
            total_pages: action.payload.total_pages,
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
