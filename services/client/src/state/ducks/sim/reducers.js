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
  LOAD_SIM_FROM_FILE,
  RESET_SIM,
} from './types'

const initialState = {
  isInitialised: false,
  isSimulated: false,
  displayUserCurve: true,
  results: {
    isLoading: false,
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
          isSimulated: false,
          results: { ...initialState.results },
        })
      }
      if (action.status === 'success') {
        // set new alloy
        return ({
          ...state,
          isInitialised: true,
          alloys: {
            ...state.alloys,
            [action.alloyType]: action.alloy,
            isLoading: false,
          },
          isSimulated: false,
          results: { ...initialState.results },
        })
      }
      if (action.status === 'fail') {
        return {
          ...state,
          alloys: {
            ...state.alloys,
            isLoading: false,
          },
          isSimulated: false,
          results: { ...initialState.results },
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
        isSimulated: false,
        results: { ...initialState.results },
      }
    case UPDATE_COMP: {
      // set new alloy
      return ({
        ...state,
        alloys: {
          ...state.alloys,
          parentError: action.parentError,
          [action.alloyType]: action.alloy,
        },
        isSimulated: false,
        results: { ...initialState.results },
      })
    }
    case UPDATE_DILUTION:
      return {
        ...state,
        alloys: {
          ...state.alloys,
          dilution: action.payload,
        },
        isSimulated: false,
        results: { ...initialState.results },
      }
    case UPDATE_CONFIG_METHOD: {
      return {
        ...state,
        configurations: {
          ...state.configurations,
          method: action.payload,
        },
        isSimulated: false,
        results: { ...initialState.results },
      }
    }
    case UPDATE_CONFIG:
      return {
        ...state,
        configurations: {
          ...state.configurations,
          ...action.payload,
        },
        isSimulated: false,
        results: { ...initialState.results },
      }
    case UPDATE_DISPLAY_USER_CURVE:
      return {
        ...state,
        displayUserCurve: action.payload,
      }
    case RUN_SIM: {
      if (action.status === 'started') {
        return {
          ...state,
          results: {
            ...state.results,
            isLoading: true,
          },
        }
      }
      if (action.status === 'fail') {
        return {
          ...state,
          results: {
            ...state.results,
            isLoading: false,
          },
        }
      }
      if (action.status === 'success' && state.results.isLoading) {
        return {
          ...state,
          isSimulated: true,
          results: {
            ...state.results,
            ...action.payload,
            isLoading: false,
            cctIndex: 0,
          },
        }
      }
      break
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
        ...initialState,
        isInitialised: true,
        isSimulated: true,
        displayUserCurve: true,
        configurations: {
          error: {},
          ...configurations,
        },
        alloys: {
          parentError: {},
          isLoading: false,
          ...alloys,
        },
        results: {
          cctIndex: 0,
          isLoading: false,
          ...results,
        },
      }
    }
    case LOAD_SIM_FROM_FILE: {
      const { alloys, configurations, results } = action.payload
      return {
        ...initialState,
        isInitialised: true,
        isSimulated: true,
        displayUserCurve: true,
        configurations: {
          error: {},
          ...configurations,
        },
        alloys: {
          parentError: {},
          isLoading: false,
          ...alloys,
        },
        results: {
          cctIndex: 0,
          isLoading: false,
          ...results,
        },
      }
    }
    case LOAD_PERSISTED_SIM:
      return action.payload
    case LOAD_LAST_SIM: {
      const {
        last_alloy_store,
        last_configuration,
        last_simulation_invalid_fields,
        last_simulation_results,
      } = action.payload
      return {
        ...initialState,
        isInitialised: Object.keys(last_alloy_store.alloys.parent).length !== 0,
        isSimulated:
          last_simulation_results && last_simulation_results.TTT
          && Object.keys(last_simulation_results.TTT).length !== 0,
        displayUserCurve: true,
        configurations: {
          ...initialState.configurations,
          error: last_simulation_invalid_fields.invalid_configs,
          ...last_configuration,
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
    case RESET_SIM:
      return {
        ...initialState,
      }
    default:
      return state
  }
}

export default reducer
