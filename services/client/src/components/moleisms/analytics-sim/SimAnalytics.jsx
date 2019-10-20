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
import { getSimulationData } from '../../../api/Analytics'
import {
  SavedAlloysSimilarity,
  MethodsHorizontalBarChart,
  SavedAlloysByNameHorizontalChart
} from '../charts'

import styles from './SimAnalytics.module.scss'


class SimAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: false,
      isLoadingSavedAlloySimilarity: false,
      alloysTSNEData: undefined,
      methodsData: undefined,
      savedAlloysByNameData: undefined,
    }
  }

  componentDidMount = () => {
    this.setState({
      isLoading: true,
      isLoadingSavedAlloySimilarity: true
    })
    this.fetchSavedAlloysSimilarity()
    this.fetchMethodsData()
    this.fetchSavedAlloysByNameData()
  }

  fetchMethodsData = () => {
    getSimulationData('/sim/methods_data').then((res) => {
      this.setState({
        methodsData: res.data,
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

  fetchSavedAlloysByNameData = () => {
    getSimulationData('/sim/saved_alloys_name_count').then((res) => {
      this.setState({
        savedAlloysByNameData: res.data,
        isLoading: false,
      })
    })
      .catch((err) => logError(
        err.toString(),
        err.message,
        'SimAnalytics.fetchSavedAlloysByNameData',
        err.stack
      ))
  }

  fetchSavedAlloysSimilarity = () => {
    getSimulationData('/sim/saved_alloys_similarity').then((res) => {
      this.setState({
        alloysTSNEData: res.data,
        isLoadingSavedAlloySimilarity: false,
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
    const {
      alloysTSNEData,
      methodsData,
      savedAlloysByNameData,
      isLoading,
      isLoadingSavedAlloySimilarity,
    } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - Simulations</h3>

        <h5>What methods are used in simulations?</h5>
        <div className={styles.methodsChart}>
          <Card className={styles.chartCard}>
            <div>
              <MethodsHorizontalBarChart
                isLoading={isLoading}
                data={(methodsData !== undefined) ? methodsData : undefined}
              />
            </div>
          </Card>
        </div>

        <h5>What alloys are used in simulations?</h5>
        <div className={styles.savedAlloysNameChart}>
          <Card className={styles.savedAlloysNameCard}>
            <div>
              <SavedAlloysByNameHorizontalChart
                isLoading={isLoading}
                data={(savedAlloysByNameData !== undefined) ? savedAlloysByNameData : undefined}
              />
            </div>
          </Card>
        </div>

        <h5>What similarities do alloys saved by users have?</h5>
        <div className={styles.chart}>
          <Card className={styles.alloysTSNEChart}>
            <div>
              <SavedAlloysSimilarity
                isLoading={isLoadingSavedAlloySimilarity}
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
