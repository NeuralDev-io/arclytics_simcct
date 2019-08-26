import {
  GET_PERSIST_USER_STATUS,
} from './types'

const initialState = {
  userStatus: {
    admin: false,
    isProfile: false,
    verified: false,
  },
}

const reducer = (state = initialState, action) => {
  if (action.type === GET_PERSIST_USER_STATUS) {
    return {
      ...state,
      userStatus: {
        ...state.user,
        ...action.payload,
      },
    }
  }
  return state
}

export default reducer
