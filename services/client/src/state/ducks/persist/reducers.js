import { PERSIST_SIM } from './types'

const initialState = {
  lastSim: {},
  lastSimTime: '',
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case PERSIST_SIM:
      return {
        ...state,
        lastSim: action.payload,
        lastSimTime: action.time,
      }
    default:
      return state
  }
}

export default reducer
