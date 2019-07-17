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
import CompSidebar from '../../moleisms/composition'

import styles from './SimulationPage.module.scss'

class SimulationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      configurations: {
        method: 'Li98',
        alloy: 'parent',
        grain_size_type: 'ASTM',
        grain_size: 8.0,
        nucleation_start: 1.0,
        nucleation_finish: 99.9,
        auto_calculate_xfe: true,
        xfe_value: 0.0,
        cf_value: 0.012,
        ceut_value: 0.762,
        auto_calculate_ms_bs: true,
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
      compositions: [],
      composition: '',
    }
  }

  componentDidMount = () => {
  }

  handleCompChange = (name, value) => {
    const { alloys } = this.props

    if (name === 'alloy') { // alloy type is changed
      if (value === null) {
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            alloy: '',
          },
        }))
      } else {
        this.setState(prevState => ({
          configurations: {
            ...prevState.configurations,
            alloy: value.value,
          },
        }))
      }
    } else if (name === 'composition') { // composition is changed
      if (value === null) {
        // clear all elements
        this.setState({
          composition: '',
          compositions: [],
        })
      } else {
        // find composition and set to state
        this.setState({
          composition: value.value,
          compositions: [
            ...alloys[alloys.findIndex(a => a.name === value.value)].compositions,
          ],
        })
      }
    } else { // weight of an element is changed
      this.setState((prevState) => {
        console.log(name, value)
        const idx = prevState.compositions.findIndex(elem => elem.name === name)
        const newComp = [...prevState.compositions]
        if (idx !== undefined) {
          newComp[idx] = {
            ...newComp[idx],
            weight: value,
          }
        }
        return {
          compositions: newComp,
        }
      })
    }
  }

  render() {
    const { configurations, compositions, composition } = this.state

    return (
      <div className={styles.outer}>
        <div className={styles.compSidebar}>
          <CompSidebar
            values={{
              alloy: configurations.alloy,
              composition,
              compositions,
            }}
            onChange={this.handleCompChange}
          />
        </div>
      </div>
    )
  }
}

SimulationPage.propTypes = {
  alloys: PropTypes.arrayOf(PropTypes.shape({
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
  alloys: state.alloys.list,
})

export default connect(mapStateToProps, {})(SimulationPage)
