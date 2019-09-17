import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
  UPDATE_EMAIL,
  CHANGE_PASSWORD,
  SAVE_SIM,
  GET_SIM,
} from './types'

const initialState = {
  user: {
    admin: false,
    profile: {
      aim: '',
      highest_education: '',
      sci_tech_exp: '',
      phase_transform_exp: '',
    },
  },
  savedSimulations: [],
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_USER_PROFILE:
      return {
        user: {
          ...state.user,
          ...action.payload,
        },
      }
    case CREATE_USER_PROFILE:
      return {
        ...state,
        user: {
          ...state.user,
          profile: {
            ...state.profile,
            ...action.payload,
          },
        },
      }
    case UPDATE_USER_PROFILE:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload,
        },
      }
    case UPDATE_EMAIL:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload,
        },
      }
    case CHANGE_PASSWORD:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload,
        },
      }
    case SAVE_SIM:
      return {
        ...state,
        savedSimulations: [
          ...state.savedSimulations,
          action.payload,
        ],
      }
    case GET_SIM:
      return {
        ...state,
        savedSimulations: [...action.payload],
      }
    default:
      return state
  }
}

export default reducer
