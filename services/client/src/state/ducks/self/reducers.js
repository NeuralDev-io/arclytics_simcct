import {
  GET_USER_PROFILE,
  CREATE_USER_PROFILE,
  UPDATE_USER_PROFILE,
  UPDATE_EMAIL,
  SAVE_SIM,
  GET_SIM,
  GET_LAST_SIM,
  DELETE_SIM,
  UPDATE_PASSWORD,
} from './types'
import { SUPPORTED_THEMES } from '../../../utils/theming'

const initialState = {
  user: {
    isFetched: false,
    admin: false,
    profile: {
      aim: '',
      highest_education: '',
      sci_tech_exp: '',
      phase_transform_exp: '',
    },
    email: '',
    first_name: '',
    last_name: '',
    active: false,
    verified: false,
    last_updated: '',
    last_login: '',
    created: '',
    // when user editing email or password
    isEmailUpdating: false,
    isPasswordUpdating: false,
  },
  savedSimulations: {
    fetched: false,
    isLoading: false,
    data: [],
  },
  lastSim: {},
  // default theme when the app starts is the theme stored in localStorage
  // if theme in localStorage is invalid then default it to light
  theme: 'light',
}

/**
 * This function gets the theme from localStorage.
 * If theme is invalid, it sets theme in localStorage to default
 * as 'light
 */
const getStorageTheme = () => {
  const theme = localStorage.getItem('theme') || ''
  if (!SUPPORTED_THEMES.includes(theme)) {
    localStorage.setItem('theme', 'light')
    return 'light'
  }
  return theme
}

const reducer = (
  state = {
    ...initialState,
    theme: getStorageTheme(),
  },
  action,
) => {
  switch (action.type) {
    case GET_USER_PROFILE:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload,
          isFetched: true,
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
    case UPDATE_EMAIL: {
      if (action.status === 'started') {
        return {
          ...state,
          user: {
            ...state.user,
            isEmailUpdating: true,
          },
        }
      }
      if (action.status === 'success') {
        return {
          ...state,
          user: {
            ...state.user,
            email: action.payload,
            isEmailUpdating: false,
          },
        }
      }
      if (action.status === 'fail') {
        return {
          ...state,
          user: {
            ...state.user,
            isEmailUpdating: false,
          },
        }
      }
      break
    }
    case UPDATE_PASSWORD: {
      if (action.status === 'started') {
        return {
          ...state,
          user: {
            ...state.user,
            isPasswordUpdating: true,
          },
        }
      }
      if (action.status === 'started') {
        return {
          ...state,
          user: {
            ...state.user,
            isPasswordUpdating: false,
          },
        }
      }
      break
    }
    case SAVE_SIM:
      return {
        ...state,
        savedSimulations: {
          ...state.savedSimulations,
          data: [
            ...state.savedSimulations.data,
            action.payload,
          ],
        },
      }
    case GET_SIM: {
      if (action.status === 'started') {
        return {
          ...state,
          savedSimulations: {
            ...state.savedSimulations,
            isLoading: true,
          },
        }
      }
      if (action.status === 'success') {
        return {
          ...state,
          savedSimulations: {
            ...state.savedSimulations,
            fetched: true,
            isLoading: false,
            data: [
              ...action.payload,
            ],
          },
        }
      }
      if (action.status === 'fail') {
        return {
          ...state,
          savedSimulations: {
            ...state.savedSimulations,
            isLoading: false,
            data: [],
          },
        }
      }
      break
    }
    case DELETE_SIM: {
      return {
        ...state,
        savedSimulations: {
          ...state.savedSimulations,
          data: state.savedSimulations.data.filter(sim => sim._id !== action.payload), // eslint-disable-line
        },
      }
    }
    case GET_LAST_SIM:
      return {
        ...state,
        lastSim: action.payload,
      }
    case 'self/CHANGE_THEME':
      return {
        ...state,
        theme: action.payload,
      }
    default:
      return state
  }
}

export default reducer
