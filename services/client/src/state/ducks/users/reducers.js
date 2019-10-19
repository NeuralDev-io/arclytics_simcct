import {
  GET_USERS,
  PROMOTE_ADMIN,
  DEACTIVATE_USER,
  ENABLE_USER,
} from './types'

const initialState = []

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_USERS:
      return [...action.payload]
    case PROMOTE_ADMIN:
      return state
    case DEACTIVATE_USER:
      return state
    case ENABLE_USER:
      const newUsers = [...state]
      const idx = newUsers.findIndex(a => a.email === action.payload)
      newUsers[idx].active = true
      return newUsers
    default:
      return state
  }
}

export default reducer
