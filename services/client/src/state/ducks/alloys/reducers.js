import {
  GET_GLOBAL_ALLOYS,
  CREATE_GLOBAL_ALLOY,
  UPDATE_GLOBAL_ALLOY,
  DELETE_GLOBAL_ALLOY,
  GET_USER_ALLOYS,
  CREATE_USER_ALLOY,
  UPDATE_USER_ALLOY,
  DELETE_USER_ALLOY,
} from './types'

const initialState = {
  global: {
    isFetched: false,
    isLoading: false,
    data: [],
  },
  user: {
    isFetched: false,
    isLoading: false,
    data: [],
  },
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_GLOBAL_ALLOYS: {
      if (action.status === 'started') {
        return {
          ...state,
          global: {
            ...state.global,
            isLoading: true,
          },
        }
      }
      if (action.status === 'success') {
        return {
          ...state,
          global: {
            ...state.global,
            isLoading: false,
            isFetched: true,
            data: action.payload,
          },
        }
      }
      if (action.status === 'fail') {
        return {
          ...state,
          global: {
            ...state.global,
            isLoading: false,
          },
        }
      }
      break
    }
    case CREATE_GLOBAL_ALLOY: {
      const newAlloys = [
        ...state.global.data,
        action.payload,
      ]
      return {
        ...state,
        global: {
          ...state.global,
          data: newAlloys,
        },
      }
    }
    case UPDATE_GLOBAL_ALLOY: {
      return {
        ...state,
        global: {
          ...state.global,
          data: state.global.data.map((alloy) => {
            if (alloy._id === action.payload._id) { // eslint-disable-line
              return {
                ...alloy,
                ...action.payload,
              }
            }
            return alloy
          }),
        },
      }
    }
    case DELETE_GLOBAL_ALLOY: {
      const newAlloys = state.global.data.filter(a => a._id !== action.payload) // eslint-disable-line
      return {
        ...state,
        global: {
          ...state.global,
          data: newAlloys,
        },
      }
    }
    case GET_USER_ALLOYS: {
      if (action.status === 'started') {
        return {
          ...state,
          user: {
            ...state.user,
            isLoading: true,
          },
        }
      }
      if (action.status === 'success') {
        return {
          ...state,
          user: {
            ...state.user,
            isLoading: false,
            isFetched: true,
            data: action.payload,
          },
        }
      }
      if (action.status === 'fail') {
        return {
          ...state,
          user: {
            ...state.user,
            isLoading: false,
          },
        }
      }
      break
    }
    case CREATE_USER_ALLOY: {
      const newAlloys = [
        ...state.user.data,
        action.payload,
      ]
      return {
        ...state,
        user: {
          ...state.user,
          data: newAlloys,
        },
      }
    }
    case UPDATE_USER_ALLOY: {
      return {
        ...state,
        user: {
          ...state.user,
          data: state.global.data.map((alloy) => {
            if (alloy._id === action.payload._id) { // eslint-disable-line
              return {
                ...alloy,
                ...action.payload,
              }
            }
            return alloy
          }),
        },
      }
    }
    case DELETE_USER_ALLOY: {
      const newAlloys = state.user.data.filter(a => a._id !== action.payload) // eslint-disable-line
      return {
        ...state,
        user: {
          ...state.user,
          data: newAlloys,
        },
      }
    }
    default:
      return state
  }
}

export default reducer
