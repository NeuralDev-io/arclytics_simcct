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
    offset: 0,
    sort: '-created_date',
    limit: 10,
    next_offset: undefined,
    prev_offset: undefined,
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
            offset: action.payload.offset,
            sort: action.payload.sort,
            limit: action.payload.limit,
            next_offset: action.payload.next_offset,
            prev_offset: action.payload.prev_offset,
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
