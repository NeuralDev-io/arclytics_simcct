import {
  RUN_SIM,
} from './types'

const initialState = {}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case RUN_SIM:
      return {
        ...state,
        results: action.payload,
      }
    default:
      return state
  }
}

export default reducer
