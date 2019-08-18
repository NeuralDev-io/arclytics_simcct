import {
  GET_USERS,
} from './types'

const initialState = []

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_USERS:
      return [...action.payload]
    default:
      return state
  }
}

export default reducer
