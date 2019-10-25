import {
  UPDATE_FEEDBACK,
  CLOSE_FEEDBACK,
  RESET_FEEDBACK,
  GET_FEEDBACK,
  SEARCH_FEEDBACK,
} from './types'

const initialState = {
  feedbackList: [],
  isFetched: false,
  isLoading: false,
  totalPages: -1,
  sort: 'created_date',
  limit: 10,
  searchData: {
    query: '',
  },
  feedbackVisible: false,
  ratingVisible: false,
  backdrop: false,
  givingFeedback: false,
  category: '',
  rate: -1,
  message: '',
}

// eslint-disable-next-line consistent-return
const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_FEEDBACK: {
      // Ensure that subscribers know the process has started.
      if (action.status === 'started') {
        return {
          ...state,
          isLoading: true,
          isFetched: false,
        }
      }
      // Let's deal with failure first so we can get over it faster (i.e. fail fast)
      if (action.status === 'fail') {
        return {
          ...state,
          isLoading: false,
          isFetched: false,
        }
      }
      // If action.status === 'success'
      if (action.status === 'success') {
        return {
          ...state,
          feedbackList: action.payload.data || [],
          isLoading: false,
          isFetched: true,
          totalPages: action.payload.total_pages || initialState.totalPages,
          sort: action.payload.sort || initialState.sort,
          limit: action.payload.limit || initialState.limit,
        }
      }
      break
    }
    case SEARCH_FEEDBACK: {
      // Ensure that subscribers know the process has started.
      if (action.status === 'started') {
        return {
          ...state,
          isLoading: true,
          isFetched: false,
          searchData: {
            ...state.searchData,
          },
        }
      }
      // Let's deal with failure first so we can get over it faster (i.e. fail fast)
      if (action.status === 'fail') {
        return {
          ...state,
          isLoading: false,
          isFetched: false,
          searchData: {
            ...state.searchData,
          },
        }
      }
      // If action.status === 'success'
      if (action.status === 'success') {
        return {
          ...state,
          feedbackList: action.payload.data || [],
          isLoading: false,
          isFetched: true,
          totalPages: action.payload.total_pages || initialState.totalPages,
          sort: action.payload.sort || initialState.sort,
          limit: action.payload.limit || initialState.limit,
          searchData: {
            ...state.searchData,
            query: action.payload.query || initialState.searchData.query,
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
