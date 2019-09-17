import {
  GET_GLOBAL_ALLOYS,
  CREATE_GLOBAL_ALLOY,
  UPDATE_GLOBAL_ALLOY,
  DELETE_GLOBAL_ALLOY,
  GET_USER_ALLOYS,
  CREATE_USER_ALLOY,
  UPDATE_USER_ALLOY,
  DELETE_USER_ALLOY,
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
    case GET_USER_ALLOYS:
      return {
        ...state,
        user: action.payload,
      }
    case CREATE_USER_ALLOY: {
      const newAlloys = [
        ...state.user,
        action.payload,
      ]
      return {
        ...state,
        user: newAlloys,
      }
    }
    case UPDATE_USER_ALLOY: {
      const newAlloys = [...state.user]
      const idx = newAlloys.findIndex(a => a._id === action.payload._id) // eslint-disable-line
      newAlloys[idx] = action.payload
      return {
        ...state,
        user: newAlloys,
      }
    }
    case DELETE_USER_ALLOY: {
      const newAlloys = state.user.filter(a => a._id !== action.payload) // eslint-disable-line
      return {
        ...state,
        user: newAlloys,
      }
    }
    default:
      return state
  }
}

export default reducer
