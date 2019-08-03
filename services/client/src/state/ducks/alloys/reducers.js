import {
  GET_ALLOYS,
  CREATE_ALLOY,
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
    case CREATE_ALLOY: {
      const newAlloys = [
        ...state.list,
        action.payload,
      ]
      return {
        ...state,
        list: newAlloys,
      }
    }
    default:
      return state
  }
}

export default reducer
