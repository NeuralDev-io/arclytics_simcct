import {
  ADD_SIM,
  REMOVE_SIM,
  GO_FORWARD,
  GO_BACKWARD,
  SET_SIM_DATA,
  GO_TO_POINT,
} from './types'

const CAPACITY = 10

const initialState = {
  data: [],
  current: -1,
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case ADD_SIM: {
      const newData = [...state.data]
      // remove all sim after current position
      newData.splice(state.current + 1)
      // if capacity is maxed, remove the oldest sim
      if (newData.length === CAPACITY) {
        newData.shift()
      }
      // add new sim
      newData.push({
        sim: action.payload,
        timestamp: action.timestamp,
      })
      return {
        ...state,
        data: newData,
        current: newData.length - 1,
      }
    }
    case REMOVE_SIM: {
      const newData = [...state.data]
      newData.shift()
      return {
        ...state,
        data: newData,
      }
    }
    case SET_SIM_DATA:
      return {
        ...state,
        data: action.payload,
      }
    case GO_FORWARD:
      return {
        ...state,
        current: state.current + 1,
      }
    case GO_BACKWARD:
      return {
        ...state,
        current: state.current - 1,
      }
    case GO_TO_POINT:
      return {
        ...state,
        current: action.payload,
      }
    default:
      return state
  }
}

export default reducer
