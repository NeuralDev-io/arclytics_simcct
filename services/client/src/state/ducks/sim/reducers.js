import {
  RUN_SIM,
  INIT_SESSION,
  UPDATE_COMP,
  UPDATE_ALLOY_OPTION,
  UPDATE_DILUTION,
  UPDATE_CONFIG_METHOD,
  UPDATE_CONFIG,
  UPDATE_DISPLAY_USER_CURVE,
  UPDATE_CCT_INDEX,
  LOAD_SIM,
  LOAD_PERSISTED_SIM,
  LOAD_LAST_SIM,
} from './types'

const initialState = {
  isInitialised: false,
  isSimulated: false,
  displayUserCurve: true,
  results: {
    USER: {
      user_cooling_curve: {
        time: [],
        temp: [],
      },
      user_phase_fraction_data: {
        austenite: [],
        ferrite: [],
        pearlite: [],
        bainite: [],
        martensite: [],
      },
    },
    cctIndex: -1,
  },
  configurations: {
    error: {},
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
    parentError: {},
    isLoading: false,
    alloyOption: 'single',
    parent: {
      _id: '',
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
          parentError: action.parentError,
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
        isSimulated: true,
        results: {
          ...state.results,
          ...action.payload,
          cctIndex: 0,
        },
      }
    case UPDATE_CCT_INDEX:
      return {
        ...state,
        results: {
          ...state.results,
          cctIndex: action.payload,
        },
      }
    case LOAD_SIM: {
      const { alloys, configurations, results } = action.payload
      return {
        isInitialised: true,
        isSimulated: true,
        displayUserCurve: true,
        configurations: {
          error: {},
          ...configurations,
        },
        alloys: {
          isLoading: false,
          dilution: 0,
          ...alloys,
          weld: {
            _id: '',
            name: '',
            compositions: [],
          },
          mix: [],
        },
        results: {
          cctIndex: 0,
          ...results,
        },
      }
    }
    case LOAD_PERSISTED_SIM:
      return action.payload
    case LOAD_LAST_SIM: {
      const {
        last_alloy_store,
        last_configurations,
        last_simulation_invalid_fields,
        last_simulation_results,
      } = action.payload
      return {
        ...initialState,
        configurations: {
          ...initialState.configurations,
          error: last_simulation_invalid_fields.invalid_configs,
          ...last_configurations,
        },
        alloys: {
          ...initialState.alloys,
          parentError: last_simulation_invalid_fields.invalid_alloy_store,
          parent: last_alloy_store.alloys.parent,
          alloyOption: last_alloy_store.alloy_option,
        },
        results: {
          ...initialState.results,
          ...last_simulation_results,
        },
      }
    }
    default:
      return state
  }
}

export default reducer
