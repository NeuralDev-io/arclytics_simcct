import {
  RUN_SIM,
  INIT_SESSION,
  UPDATE_COMP,
  UPDATE_ALLOY_OPTION,
  UPDATE_DILUTION,
  UPDATE_CONFIG_METHOD,
  UPDATE_CONFIG,
  UPDATE_DISPLAY_USER_CURVE,
} from './types'

const initialState = {
  isInitialised: false,
  displayUserCurve: true,
  results: {},
  configurations: {
    method: 'Li98',
    grain_size_ASTM: 8.0,
    grain_size_diameter: 0.202,
    nucleation_start: 1.0,
    nucleation_finish: 99.9,
    auto_calculate_bs: true,
    auto_calculate_ms: true,
    ms_rate_param: 0.0168,
    ms_temp: 0.0,
    bs_temp: 0.0,
    auto_calculate_ae: true,
    ae1_temp: 0.0,
    ae3_temp: 0.0,
    start_temp: 900,
    cct_cooling_rate: 10,
  },
  alloys: {
    isLoading: false,
    alloyOption: 'single',
    parent: {
      id: '',
      name: '',
      compositions: [],
    },
    weld: {
      _id: '',
      name: '',
      compositions: [],
    },
    mix: [],
    dilution: 0,
  },
}

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case INIT_SESSION: {
      if (action.status === 'started') {
        return ({
          ...state,
          alloys: {
            ...state.alloys,
            isLoading: true,
          },
        })
      }
      if (action.status === 'success') {
        // set new alloy and auto-calculated fields in state
        return ({
          ...state,
          isInitialised: true,
          alloys: {
            ...state.alloys,
            [action.alloyType]: action.alloy,
            isLoading: false,
          },
          configurations: {
            ...state.configurations,
            ...action.config,
          },
        })
      }
      if (action.status === 'fail') {
        return {
          ...state,
          alloys: {
            ...state.alloys,
            isLoading: false,
          },
        }
      }
      break
    }
    case UPDATE_ALLOY_OPTION:
      return {
        ...state,
        alloys: {
          ...state.alloys,
          alloyOption: action.payload,
        },
      }
    case UPDATE_COMP:
      // set new alloy comp and auto-calculated fields in state
      return ({
        ...state,
        alloys: {
          ...state.alloys,
          [action.alloyType]: action.alloy,
        },
        configurations: {
          ...state.configurations,
          ...action.config,
        },
      })
    case UPDATE_DILUTION:
      return {
        ...state,
        alloys: {
          ...state.alloys,
          dilution: action.payload,
        },
      }
    case UPDATE_CONFIG_METHOD:
      return {
        ...state,
        configurations: {
          ...state.configurations,
          method: action.payload,
        },
      }
    case UPDATE_CONFIG:
      return {
        ...state,
        configurations: {
          ...state.configurations,
          ...action.payload,
        },
      }
    case UPDATE_DISPLAY_USER_CURVE:
      return {
        ...state,
        displayUserCurve: action.payload,
      } 
    case RUN_SIM:
      return {
        ...state,
        results: action.payload,
      }
    default:
      return state
  }
}

export default reducer
