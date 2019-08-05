import {
  GET_USER_PROFILE,
} from './types'

const initialState = {
  user: {
    admin: false,
  },
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_USER_PROFILE:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload,
        },
      }
    default:
      return state
  }
}

export default reducer
