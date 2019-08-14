import {
  GET_GLOBAL_ALLOYS,
  CREATE_GLOBAL_ALLOY,
  UPDATE_GLOBAL_ALLOY,
  DELETE_GLOBAL_ALLOY,
} from './types'

const initialState = {
  global: [],
  user: [],
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_GLOBAL_ALLOYS:
      return {
        ...state,
        global: action.payload,
      }
    case CREATE_GLOBAL_ALLOY: {
      const newAlloys = [
        ...state.global,
        action.payload,
      ]
      return {
        ...state,
        global: newAlloys,
      }
    }
    case UPDATE_GLOBAL_ALLOY: {
      const newAlloys = [...state.global]
      const idx = newAlloys.findIndex(a => a._id === action.payload._id) // eslint-disable-line
      newAlloys[idx] = action.payload
      return {
        ...state,
        global: newAlloys,
      }
    }
    case DELETE_GLOBAL_ALLOY: {
      const newAlloys = state.global.filter(a => a._id !== action.payload) // eslint-disable-line
      return {
        ...state,
        global: newAlloys,
      }
    }
    default:
      return state
  }
}

export default reducer
