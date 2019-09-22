import { PERSIST_SIM } from './types'

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
    default:
      return state
  }
}

export default reducer
