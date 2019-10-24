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
  totalPages: -1,
  sort: 'created_date',
  limit: 10,
  skip: -1,
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
        }
      }
      // Let's deal with failure first so we can get over it faster (i.e. fail fast)
      if (action.status === 'fail') {
        return {
          ...state,
          isLoading: false,
        }
      }
      // Success
      return {
        ...state,
        usersList: action.payload.data,
        isLoading: false,
        isFetched: true,
        totalPages: action.payload.total_pages,
        sort: action.payload.sort,
        limit: action.payload.limit,
        skip: action.payload.skip,
      }
    }
    case SEARCH_USERS: {
      // Ensure that subscribers know the process has started.
      if (action.status === 'started') {
        return {
          ...state,
          isLoading: true,
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
          usersList: action.payload.data,
          isLoading: false,
          isFetched: true,
          totalPages: action.payload.total_pages,
          sort: action.payload.sort,
          limit: action.payload.limit,
          skip: action.payload.skip,
          searchData: {
            ...state.searchData,
            query: action.payload.query,
          },
        }
      }
      break
    }
    case PROMOTE_ADMIN: {
      const newUsers = [...state.usersList]
      const id = newUsers.findIndex(a => a.email === action.payload.email)
      newUsers[id].admin = true
      newUsers[id].admin_profile = {
        position: action.payload.position, mobile_number: null, verified: true,
      }
      return {
        ...state,
        usersList: newUsers,
      }
    }
    case DEACTIVATE_USER:
      return {
        ...state,
      }
    case ENABLE_USER: {
      const newUsers = [...state.usersList]
      const idx = newUsers.findIndex(a => a.email === action.payload)
      newUsers[idx].active = true
      return {
        ...state,
        usersList: newUsers,
      }
    }
    default:
      return state
  }
}

export default reducer
