import {
  GET_ALLOYS,
} from './types'

const initialState = {
  list: [],
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_ALLOYS:
      return {
        ...state,
        list: action.payload,
      }
    default:
      return state
  }
}

export default reducer
