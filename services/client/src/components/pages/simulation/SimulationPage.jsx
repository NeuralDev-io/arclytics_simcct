/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Composition sidebar
 *
 * @version 0.0.0
 * @author Dalton Le
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
import Button from '../../elements/button'
import AppBar from '../../moleisms/appbar'
import CompSidebar from '../../moleisms/composition'
import { ConfigForm, UserProfileConfig } from '../../moleisms/sim-configs'
import { TTT, CCT } from '../../moleisms/charts'
import { initComp, updateComp, updateConfig } from '../../../api/sim/SessionConfigs'
import { runSim } from '../../../state/ducks/sim/actions'

import styles from './SimulationPage.module.scss'

class SimulationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      displayConfig: true,
      displayProfile: true,
      displayUserCurve: true,
      configurations: {
        method: 'Li98',
        grain_size_ASTM: 8.0,
        grain_size_diameter: 0.202,
        nucleation_start: 1.0,
        nucleation_finish: 99.9,
        auto_calculate_xfe: true,
        xfe_value: 0.0,
        cf_value: 0.012,
        ceut_value: 0.762,
        auto_calculate_bs: true,
        auto_calculate_ms: true,
        ms_rate: 5.378,
        transformation_method: 'Li98',
        ms_temp: 0.0,
        ms_undercool: 100.0,
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
    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem('token')) {
      this.props.history.push('/signin') // eslint-disable-line
    }
    initComp('single', 'parent', {
      name: '',
      compositions: [],
    })
  }

  handleCompChange = (name, value) => {
    const { alloyList } = this.props

    if (name === 'alloyOption') { // alloy option is changed
      this.setState(prevState => ({
        alloys: {
          ...prevState.alloys,
          alloyOption: value.value,
        },
      }))
      updateComp('', {})
    } else if (name === 'parent' || name === 'weld') { // alloy composition is changed
      if (value === null) {
        // clear all elements
        this.setState(prevState => ({
          alloys: {
            ...prevState.alloys,
            parent: {
              name: '',
              compositions: [],
            },
          },
        }))
      } else {
        // find composition and set to state
        this.setState(prevState => ({
          alloys: {
            ...prevState.alloys,
            [name]: {
              name: value.value,
              compositions: [
                ...alloyList[alloyList.findIndex(a => a.name === value.value)].compositions,
              ],
            },
          },
        }))
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
      this.setState((prevState) => {
        const idx = prevState.alloys[nameArr[0]].compositions.findIndex(
          elem => elem.symbol === nameArr[1]
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
    }
  }

  handleConfigChange = (name, value) => {
    if (name === 'method' || name === 'transformation_method') {
      // check if new value is null (select option was cleared)
      if (value === null) {
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            [name]: '',
          },
        }))
      } else {
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            [name]: value.value,
          },
        }))
      }
    } else if (name === 'grain_size_ASTM') {
      if (value === '') {
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: '',
            grain_size_diameter: '',
          },
        }))
      } else {
        // do some calculation here to convert unit of grain size
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: value,
            grain_size_diameter: value,
          },
        }))
      }
    } else if (name === 'grain_size_diameter') {
      if (value === '') {
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: '',
            grain_size_diameter: '',
          },
        }))
      } else {
        // do some calculation here to convert unit of grain size
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            grain_size_ASTM: value,
            grain_size_diameter: value,
          },
        }))
      }
    } else if (name === 'displayUserCurve') {
      this.setState(prevState => ({ displayUserCurve: !prevState.displayUserCurve }))
    } else {
      this.setState(prevState => ({
        configurations: {
          ...prevState.configurations,
          [name]: value,
        },
      }))
    }
  }

  render() {
    const {
      displayConfig,
      displayProfile,
      displayUserCurve,
      configurations,
      alloys,
    } = this.state
    const {
      runSim,
    } = this.props

    return (
      <React.Fragment>
        <AppBar active="sim" redirect={this.props.history.push} /> {/* eslint-disable-line */} 
        <div className={styles.compSidebar}>
          <CompSidebar
            values={alloys}
            onChange={this.handleCompChange}
            onSimulate={() => {
              console.log({
                configurations,
                alloys,
              })
              runSim()
            }}
          />
        </div>
        <div className={styles.main}>
          <header className={styles.config}>
            <h3>Configurations</h3>
            <Button
              appearance="text"
              onClick={() => this.setState(prevState => ({
                displayConfig: !prevState.displayConfig,
              }))}
              IconComponent={props => (
                displayConfig
                  ? <ChevronUpIcon {...props} />
                  : <ChevronDownIcon {...props} />
              )}
            >
              {displayConfig ? 'Collapse' : 'Expand'}
            </Button>
          </header>
          <div className={styles.configForm} style={{ display: displayConfig ? 'block' : 'none' }}>
            <ConfigForm
              values={configurations}
              onChange={this.handleConfigChange}
            />
          </div>
          <div className={styles.results}>
            <h3>Results</h3>
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
                <h3>User profile</h3>
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
            <div>

            </div>
          </div>
        </div>
      </React.Fragment>
    )
  }
}

SimulationPage.propTypes = {
  alloyList: PropTypes.arrayOf(PropTypes.shape({
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
}

const mapStateToProps = state => ({
  alloyList: state.alloys.list,
})

const mapDispatchToProps = {
  runSim,
}

export default connect(mapStateToProps, mapDispatchToProps)(SimulationPage)
