import { GET_EQUI_VALUES, RESET_EQUI_VALUES } from './types'

const initialState = {
  isLoading: false,
  xfe: 0,
  ceut: 0,
  cf: 0,
  plot: {},
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_EQUI_VALUES: {
      if (action.status === 'started') {
        return {
          ...state,
          isLoading: true,
        }
      }
      if (action.status === 'success') {
        return {
          ...state,
          isLoading: false,
          ...action.payload,
        }
      }
      if (action.status === 'fail') {
        return {
          ...initialState,
          isLoading: false,
        }
      }
      break
    }
    case RESET_EQUI_VALUES:
      return { ...initialState }
    default:
      return state
  }
}

export default reducer
