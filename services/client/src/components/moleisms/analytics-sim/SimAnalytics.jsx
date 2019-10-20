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
import Card from '../../elements/card'
import SavedAlloysSimilarity from '../charts/SavedAlloysSimilarity'
import { getSavedAlloysSimilarityData } from '../../../api/Analytics'

import styles from './SimAnalytics.module.scss'


class SimAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: false,
      alloysTSNEData: undefined,
      methodsData: undefined,
    }
  }

  componentDidMount = () => {
    this.setState({isLoading: true})
    this.fetchSavedAlloysSimilarity()
  }

  fetchSavedAlloysSimilarity = () => {
    getSavedAlloysSimilarityData().then((res) => {
      console.log(res.parameters)
      this.setState({
        alloysTSNEData: res.data,
        isLoading: false,
      })
    })
      .catch((err) => logError(
        err.toString(),
        err.message,
        'SimAnalytics.fetchSavedAlloysSimilarity',
        err.stack
      ))
  }

  render() {
    const { alloysTSNEData, isLoading } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - Simulations</h3>

        <h5>Methods used</h5>
        <div className={styles.chart}>
          <Card className={styles.alloysTSNEChart}>
            <div>

              <SavedAlloysSimilarity
                isLoading={isLoading}
                data={(alloysTSNEData !== undefined) ? alloysTSNEData : undefined}
              />
            </div>
          </Card>
        </div>

        <h5>Saved alloy similarities</h5>
        <div className={styles.chart}>
          <Card className={styles.alloysTSNEChart}>
            <div>

              <SavedAlloysSimilarity
                isLoading={isLoading}
                data={(alloysTSNEData !== undefined) ? alloysTSNEData : undefined}
              />
            </div>
          </Card>
        </div>
      </div>
    )
  }
}

export default SimAnalytics
