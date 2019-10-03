import {
  GET_USERS,
  PROMOTE_ADMIN
} from './types'

const initialState = []

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_USERS:
      return [...action.payload]
    case PROMOTE_ADMIN:
      return state
    default:
      return state
  }
}

export default reducer
