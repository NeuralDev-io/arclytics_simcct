import {
  ADD_FLASH_TOAST,
  REMOVE_FLASH_TOAST,
} from './types'

const initialState = {
  notifications: [],
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case ADD_FLASH_TOAST:
      return {
        ...state,
        notifications: [
          ...state.notifications,
          {
            ...action.notification,
          },
        ],
      }
    case REMOVE_FLASH_TOAST:
      return {
        ...state,
        notifications: state.notifications.filter(
          notification => notification.key !== action.key,
        ),
      }
    default:
      return state
  }
}

export default reducer
