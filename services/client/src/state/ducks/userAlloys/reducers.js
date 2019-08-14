import {
  CREATE_USER_ALLOY,
  RETRIEVE_USER_ALLOYS,
  RETRIEVE_USER_ALLOY_DETAIL,
  UPDATE_USER_ALLOY,
  DELETE_USER_ALLOY,
} from './types'

const initialState = {
  list: [], // For when the response is a list of alloys in RETRIEVE_USER_ALLOYS.
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case CREATE_USER_ALLOY: {
      // If postUserAlloy() dispatches to create a new alloy.
      console.log(action.payload)
      // eslint-disable-next-line no-case-declarations
      return {
        ...state,
        // basically just append the new alloy to the list
        list: [
          ...state.list,
          action.payload,
        ],
      }
    }
    case RETRIEVE_USER_ALLOYS:
      // If getUserAlloys() dispatches to get a list of user alloys.
      return {
        ...state,
        list: action.payload,
      }
    case RETRIEVE_USER_ALLOY_DETAIL:
      // If getUserAlloyDetail() dispatches to get a single alloy.
      return {
        ...state,
        list: [
          ...state.list,
          action.payload,
        ],
      }
    case UPDATE_USER_ALLOY:
      // TODO(andrew@neuraldev.io): This may not work.
      // If putUserAlloy() dispatches to get update and retrieve single alloy.
      return {
        ...state,
        list: [
          ...state.list,
          action.payload,
        ],
      }
    case DELETE_USER_ALLOY:
      // If deleteUserAlloy() dispatches, there's nothing to return because
      // a fail of this method would throw a new Error()
      return state
    default:
      return state
  }
}

export default reducer
