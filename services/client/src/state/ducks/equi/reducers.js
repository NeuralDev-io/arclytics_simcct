import { GET_EQUI_VALUES } from './types'

const initialState = {
  isLoading: false,
  xfe: '',
  ceut: '',
  cf: '',
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
    default:
      return state
  }
}

export default reducer
