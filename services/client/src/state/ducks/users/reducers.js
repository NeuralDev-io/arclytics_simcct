import {
  GET_USERS,
  SEARCH_USERS,
  PROMOTE_ADMIN,
  DEACTIVATE_USER,
  ENABLE_USER,
} from './types'

const initialState = {
  usersList: [],
  isFetched: false,
  isLoading: false,
  totalPages: 0,
  sort: 'created_date',
  limit: 10,
  skip: 0,
  searchData: {
    query: '',
  },
}

// eslint-disable-next-line consistent-return
const reducer = (state = initialState, action) => {
  switch (action.type) {
    case GET_USERS: {
      // Ensure that subscribers know the process has started.
      if (action.status === 'started') {
        return {
          ...state,
          isLoading: true,
          isFetched: false,
        }
      }
      // Let's deal with failure first so we can get over it faster (i.e. fail fast)
      if (action.status === 'fail') {
        return {
          ...state,
          isLoading: false,
        }
      }
      if (action.status === 'success') {
        return {
          ...state,
          usersList: action.payload.data || [],
          isLoading: false,
          isFetched: true,
          totalPages: action.payload.total_pages || initialState.totalPages,
          sort: action.payload.sort || initialState.sort,
          limit: action.payload.limit || initialState.limit,
          skip: action.payload.skip || initialState.skip,
        }
      }
      break
    }
    case SEARCH_USERS: {
      // Ensure that subscribers know the process has started.
      if (action.status === 'started') {
        return {
          ...state,
          isLoading: true,
          isFetched: false,
          searchData: {
            ...state.searchData,
          },
        }
      }
      // Let's deal with failure first so we can get over it faster (i.e. fail fast)
      if (action.status === 'fail') {
        return {
          ...state,
          isLoading: false,
          searchData: {
            ...state.searchData,
          },
        }
      }
      // If action.status === 'success'
      if (action.status === 'success') {
        return {
          ...state,
          isLoading: false,
          isFetched: true,
          // always returned from action dispatch as empty list or data
          usersList: action.payload.data || [],
          totalPages: action.payload.total_pages || initialState.totalPages,
          sort: action.payload.sort || initialState.sort,
          limit: action.payload.limit || initialState.limit,
          skip: action.payload.skip || initialState.skip,
          searchData: {
            ...state.searchData,
            query: action.payload.query || initialState.searchData.query,
          },
        }
      }
      break
    }
    case PROMOTE_ADMIN: {
      return {
        ...state,
        usersList: state.usersList.map((user) => {
          if (user.email === action.payload.email) {
            return {
              ...user,
              admin: true,
              admin_profile: {
                ...user.admin_profile,
                position: action.payload.position,
                mobile_number: null,
                verified: true,
              },
            }
          }
          return user
        }),
      }
    }
    case ENABLE_USER: {
      return {
        ...state,
        usersList: state.usersList.map((user) => {
          if (user.email === action.payload) {
            return {
              ...user,
              active: true,
            }
          }
          return user
        }),
      }
    }
    default:
      return state
  }
}

export default reducer
