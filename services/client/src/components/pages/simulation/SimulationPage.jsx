/* eslint-disable camelcase */
/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Composition sidebar
 *
 * @version 0.8.0
 * @author Dalton Le and Andrew Che
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
import Share2Icon from 'react-feather/dist/icons/share-2'
import SaveIcon from 'react-feather/dist/icons/save'
import UploadIcon from 'react-feather/dist/icons/upload'
import Button from '../../elements/button'
import AppBar from '../../moleisms/appbar'
import CompSidebar from '../../moleisms/composition'
import ShareModal from '../../moleisms/share-modal'
import { ConfigForm, UserProfileConfig } from '../../moleisms/sim-configs'
import { TTT, CCT } from '../../moleisms/charts'
import {
  initComp,
  updateComp,
  updateConfigMethod,
  updateConfig,
  updateMsBsAe,
  getMsBsAe,
} from '../../../api/sim/SessionConfigs'
import { ASTM2Dia, dia2ASTM } from '../../../utils/grainSizeConverter'
import { postSaveSimulation } from '../../../api/sim/SessionSaveSim'
import { runSim } from '../../../state/ducks/sim/actions'

import styles from './SimulationPage.module.scss'

class SimulationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      sessionStoreInit: false,
      displayConfig: true,
      displayProfile: true,
      displayUserCurve: true,
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
        alloyOption: 'single',
        parent: {
          name: '',
          compositions: [],
        },
        weld: {
          name: '',
          compositions: [],
        },
        mix: {
          name: '',
          compositions: [],
        },
        dilution: 0,
      },
      shareModal: false,
    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem('token')) {
      this.props.history.push('/signin') // eslint-disable-line
    }
  }

  handleCompChange = (name, value) => {
    const { globalAlloys } = this.props
    const { sessionStoreInit } = this.state

    if (name === 'alloyOption') { // alloy option is changed
      this.setState(prevState => ({
        alloys: {
          ...prevState.alloys,
          alloyOption: value.value,
        },
      }))
    } else if (name === 'parent' || name === 'weld') { // alloy composition is changed
      // find composition
      const alloy = {
        name: value.value,
        compositions: [
          ...globalAlloys[globalAlloys.findIndex(a => a.name === value.value)].compositions,
        ],
      }
      // update session store on the server
      const { alloys } = this.state
      // if session store is already initiated, update it
      // otherwise, initiate a new session store with new Comp and update
      // the session config
      if (sessionStoreInit) updateComp(alloys.alloyOption, name, alloy)
      else {
        initComp(alloys.alloyOption, name, alloy)
          .then(
            (data) => {
              // set to state alloy + configs
              this.setState(prevState => ({
                alloys: {
                  ...prevState.alloys,
                  [name]: alloy,
                },
                configurations: {
                  ...prevState.configurations,
                  ...data,
                },
              }))
            },
            err => console.log(err),
          )
        const { configurations } = this.state
        const {
          grain_size_ASTM,
          grain_size_diameter,
          nucleation_start,
          nucleation_finish,
          cct_cooling_rate,
        } = configurations
        updateConfig({
          grain_size_ASTM,
          grain_size_diameter,
          nucleation_start,
          nucleation_finish,
          cct_cooling_rate,
        })
        this.setState({ sessionStoreInit: true })
      }
    } else if (name === 'dilution') {
      this.setState(prevState => ({
        alloys: {
          ...prevState.alloys,
          dilution: value,
        },
      }))
    } else { // weight of an element is changed
      const nameArr = name.split('_')
      // update state
      this.setState((prevState) => {
        const idx = prevState.alloys[nameArr[0]].compositions.findIndex(
          elem => elem.symbol === nameArr[1],
        )
        const newComp = [...prevState.alloys[nameArr[0]].compositions]
        if (idx !== undefined) {
          newComp[idx] = {
            ...newComp[idx],
            weight: value,
          }
        }
        return {
          alloys: {
            ...prevState.alloys,
            [nameArr[0]]: {
              ...prevState.alloys[nameArr[0]],
              compositions: newComp,
            },
          },
        }
      })
      // update session store on the server
      if (nameArr[0] === 'parent') {
        const { alloys } = this.state
        updateComp(alloys.alloyOption, nameArr[0], {
          name: alloys[nameArr[0]].name,
          compositions: [
            {
              symbol: nameArr[1],
              weight: parseFloat(value),
            },
          ],
        })
          .then(
            (data) => {
              this.setState(prevState => ({
                configurations: {
                  ...prevState.configurations,
                  ...data,
                },
              }))
            },
            err => console.log(err),
          )
      }
    }
  }

  handleConfigChange = (name, value) => {
    if (name === 'method') {
      // set new value to state
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value.value,
        },
      }))

      // update method in session store on server
      updateConfigMethod(value.value)
    } else if (name === 'grain_size_ASTM') {
      if (value === '') {
        // set value to state
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: '',
            grain_size_diameter: '',
          },
        }))

        // update in server session store with value = 0
        updateConfig({ grain_size: 0 })
      } else {
        // convert unit of grain size
        const grainSizeDiameter = ASTM2Dia(parseFloat(value))
        // set value to state
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: value,
            grain_size_diameter: grainSizeDiameter,
          },
        }))

        // update in server session store
        updateConfig({ grain_size: parseFloat(value) })
      }
    } else if (name === 'grain_size_diameter') {
      if (value === '') {
        // set value to state
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: '',
            grain_size_diameter: '',
          },
        }))

        // update in server session store with value = 0
        updateConfig({ grain_size: 0 })
      } else {
        // convert unit of grain size
        const grainSizeASTM = dia2ASTM(parseFloat(value))
        // set value to state
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: grainSizeASTM,
            grain_size_diameter: value,
          },
        }))

        // update in server session store
        updateConfig({ grain_size: parseFloat(grainSizeASTM) })
      }
    } else if (name === 'displayUserCurve') {
      this.setState(prevState => ({ displayUserCurve: !prevState.displayUserCurve }))
    } else if (name === 'ms_temp' || name === 'ms_rate_param') {
      const { configurations } = this.state
      const data = {
        ms_temp: configurations.ms_temp,
        ms_rate_param: configurations.ms_rate_param,
      }

      // update state
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value,
        },
      }))

      // update in server session store
      updateMsBsAe('ms', {
        ...data,
        [name]: value,
      })
    } else if (name === 'bs_temp') {
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value,
        },
      }))

      // update in server session store
      updateMsBsAe('bs', { [name]: value })
    } else if (name === 'ae1_temp' || name === 'ae3_temp') {
      const { configurations } = this.state
      const data = {
        ae1_temp: configurations.ae1_temp,
        ae3_temp: configurations.ae3_temp,
      }

      // update state
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value,
        },
      }))

      // update in server session store
      updateMsBsAe('ae', {
        ...data,
        [name]: value,
      })
    } else if (name === 'auto_calculate_ms' || name === 'auto_calculate_bs'
      || name === 'auto_calculate_ae') {
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value,
        },
      }))

      // update in server session store
      const nameArr = name.split('_')
      // if auto calculate is turned ON, we have to make GET request to get
      // the new auto-calculated values. If they are turned OFF, make PUT
      // request to update the configs with custom values - quirk of the API
      if (value) {
        getMsBsAe(nameArr[2])
          .then(
            (data) => {
              this.setState(prevState => ({
                configurations: {
                  ...prevState.configurations,
                  ...data,
                },
              }))
            },
            err => console.log(err),
          )
      } else {
        // form the request body based on which of bs, ms or ae was updated
        const { configurations } = this.state
        let data = {}
        if (name === 'auto_calculate_ae') {
          data = {
            ae1_temp: configurations.ae1_temp,
            ae3_temp: configurations.ae3_temp,
          }
        }
        if (name === 'auto_calculate_bs') data = { bs_temp: configurations.bs_temp }
        if (name === 'auto_calculate_ms') {
          data = {
            ms_temp: configurations.ms_temp,
            ms_rate_param: configurations.ms_rate_param,
          }
        }
        updateMsBsAe(nameArr[2], data)
      }
    } else {
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value,
        },
      }))
      updateConfig({ [name]: value })
    }
  }

  // TODO(andrew@neuraldev.io): Just for testing.
  // Probably need to use this to do some validation checks before trying to run sim.
  runSimulation = () => {
    const { runSimConnect } = this.props
    updateConfig({
      nucleation_start: 0.0,
      nucleation_finish: 99.9,
      cct_cooling_rate: 10,
      start_temp: 900,
    })
    runSimConnect()
  }

  handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  saveCurrentSimulation = () => {
    const { configurations, alloys } = this.state
    console.log(configurations)
    const alloyStore = {
      alloy_option: alloys.alloyOption,
      alloys: {
        parent: alloys.parent,
        weld: alloys.weld,
        mix: alloys.mix,
      },
    }
    console.log(alloyStore)
    postSaveSimulation(configurations, alloyStore)
  }


  render() {
    const {
      sessionStoreInit,
      displayConfig,
      displayProfile,
      displayUserCurve,
      configurations,
      alloys,
      shareModal,
    } = this.state
    const {
      runSimConnect,
      history,
    } = this.props

    return (
      <React.Fragment>
        <AppBar active="sim" redirect={history.push} />
        <div className={styles.compSidebar}>
          <CompSidebar
            values={alloys}
            onChange={this.handleCompChange}
            storeInit={sessionStoreInit}
            onSimulate={() => {
              console.log({
                configurations,
                alloys,
              })
              this.runSimulation()
            }}
          />
        </div>
        <div className={styles.main}>
          <header>
            <div className={styles.config}>
              <h4>Configurations</h4>
              <Button
                appearance="text"
                onClick={() => this.setState(prevState => ({
                  displayConfig: !prevState.displayConfig,
                }))}
                IconComponent={(props) => {
                  if (displayConfig) return <ChevronUpIcon {...props} />
                  return <ChevronDownIcon {...props} />
                }}
              >
                {displayConfig ? 'Collapse' : 'Expand'}
              </Button>
            </div>
            <div className={styles.actions}>
              <Button
                appearance="text"
                onClick={() => this.handleShowModal('share')}
                IconComponent={props => <Share2Icon {...props} />}
              >
                SHARE
              </Button>

              <Button
                appearance="outline"
                type="button"
                onClick={this.saveCurrentSimulation}
                IconComponent={props => <SaveIcon {...props} />}
              >
                SAVE
              </Button>

              <Button
                appearance="outline"
                type="button"
                onClick={() => console.log('LOAD NOW')}
                IconComponent={props => <UploadIcon {...props} />}
              >
                LOAD
              </Button>
            </div>
          </header>
          <div className={styles.configForm} style={{ display: displayConfig ? 'block' : 'none' }}>
            <ConfigForm
              values={configurations}
              onChange={this.handleConfigChange}
            />
          </div>
          <div className={styles.results}>
            <h4>Results</h4>
            <div className={styles.charts}>
              <div className={styles.line}>
                <h5>TTT</h5>
                <TTT />
              </div>
              <div className={styles.line}>
                <h5>CCT</h5>
                <CCT />
              </div>
            </div>
          </div>
          <div className={styles.custom}>
            <div>
              <header className={styles.profile}>
                <h4>User profile</h4>
                <Button
                  appearance="text"
                  onClick={() => this.setState(prevState => ({
                    displayProfile: !prevState.displayProfile,
                  }))}
                  IconComponent={props => (
                    displayProfile
                      ? <ChevronUpIcon {...props} />
                      : <ChevronDownIcon {...props} />
                  )}
                >
                  {displayProfile ? 'Collapse' : 'Expand'}
                </Button>
              </header>
              <div style={{ display: displayProfile ? 'block' : 'none' }}>
                <UserProfileConfig
                  values={{
                    start_temp: configurations.start_temp,
                    cct_cooling_rate: configurations.cct_cooling_rate,
                    displayUserCurve,
                  }}
                  onChange={this.handleConfigChange}
                />
              </div>
            </div>
          </div>
        </div>

        <ShareModal
          show={shareModal}
          onClose={() => this.handleCloseModal('share')}
          onConfirm={() => console.log('Sharing Confirmed')}
        />
      </React.Fragment>
    )
  }
}

SimulationPage.propTypes = {
  globalAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    })),
  })).isRequired,
  runSimConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
})

const mapDispatchToProps = {
  runSimConnect: runSim,
}

export default connect(mapStateToProps, mapDispatchToProps)(SimulationPage)
