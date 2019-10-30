import { ADD_LOCATION, REMOVE_LOCATION } from './types'

const initialState = {
  locations: [],
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case ADD_LOCATION:
      return {
        ...state,
        locations: [
          ...state.locations,
          action.payload,
        ],
      }
    case REMOVE_LOCATION:
      return {
        ...state,
        locations: state.locations.filter(
          loc => loc.key !== action.payload,
        ),
      }
    default:
      return state
  }
}

export default reducer
