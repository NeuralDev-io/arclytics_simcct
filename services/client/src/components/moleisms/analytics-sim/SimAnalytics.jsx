/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Analytics specific to Simulation and Alloys data.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React, { Component } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { logError } from '../../../api/LoggingHelper'
import { getColor } from '../../../utils/theming'
import Card from '../../elements/card'
import { roundTo } from '../../../utils/math'

import styles from './SimAnalytics.module.scss'


class SimAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      alloysTSNEData: undefined,
    }
  }

  componentDidMount = () => {}

  render() {
    const { alloysTSNEData } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - Simulations</h3>

        <h5></h5>
        <div className={styles.chart}>

        </div>
      </div>
    )
  }
}

export default SimAnalytics
