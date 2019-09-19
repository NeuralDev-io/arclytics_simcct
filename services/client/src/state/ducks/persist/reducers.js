import { PERSIST_SIM, RESET } from './types'

const initialState = {
  lastSim: {},
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case PERSIST_SIM:
      return {
        ...state,
        lastSim: action.payload,
      }
    case RESET:
      return {}
    default:
      return state
  }
}

export default reducer
