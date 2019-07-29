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
import ConfigForm from '../../moleisms/sim-configs'
import { TTT } from '../../moleisms/charts'
import { updateComp, updateConfig } from '../../../utils/sim/SessionConfigs'
import { runSim } from '../../../state/ducks/sim/actions'

import styles from './SimulationPage.module.scss'

class SimulationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      displayConfig: true,
      configurations: {
        method: 'Li98',
        grain_size_type: 'ASTM',
        grain_size: 8.0,
        nucleation_start: 1.0,
        nucleation_finish: 99.9,
        auto_calculate_xfe: false,
        xfe_value: 0.0,
        cf_value: 0.012,
        ceut_value: 0.762,
        auto_calculate_ms_bs: false,
        transformation_method: 'Li98',
        ms_temp: 0.0,
        ms_undercool: 100.0,
        bs_temp: 0.0,
        auto_calculate_ae: false,
        ae1_temp: 0.0,
        ae3_temp: 0.0,
        start_temp: 900,
        cct_cooling_rate: 10,
      },
      compositions: [],
      composition: '',
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
        dialution: 0,
      },
    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem('token')) {
      this.props.history.push('/signin') // eslint-disable-line
    }
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
    } else if (name === 'dialution') {
      this.setState(prevState => ({
        alloys: {
          ...prevState.alloys,
          dialution: value,
        },
      }))
    } else { // weight of an element is changed
      const nameArr = name.split('_')
      this.setState((prevState) => {
        const idx = prevState.alloys[nameArr[0]].compositions.findIndex(elem => elem.symbol === nameArr[1])
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
    if (name === 'method' || name === 'grain_size_type' || name === 'transformation_method') {
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
          <header>
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
          <div style={{ display: displayConfig ? 'block' : 'none' }}>
            <ConfigForm
              values={configurations}
              onChange={this.handleConfigChange}
            />
          </div>
          <div className={styles.ttt}>
            <h3>Time temperature transformations</h3>
            <TTT />
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
