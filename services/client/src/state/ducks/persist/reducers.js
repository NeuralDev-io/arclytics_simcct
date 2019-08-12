import {
  GET_USER_PROFILE,
  UPDATE_USER_PROFILE
} from './types'

const initialState = {
  user: {
    first_name: 'fakeName',
    last_name: 'fakeLast',
    admin: true,
    profile: null
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
    case UPDATE_USER_PROFILE:
      return {
        ...state,
        user:{
          ...state.user,
          ...action.payload
        }
      }
    default:
      return state
  }
}

export default reducer
