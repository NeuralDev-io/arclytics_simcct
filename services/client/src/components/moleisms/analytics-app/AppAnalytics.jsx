/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Analytics specific to Application data.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { logError, logInfo } from '../../../api/LoggingHelper'
import { getColor } from '../../../utils/theming'
import Card from '../../elements/card'
import DatabaseIcon from 'react-feather/dist/icons/database'
import PlayCircleIcon from 'react-feather/dist/icons/play-circle'
import StarIcon from 'react-feather/dist/icons/star'
import LiveLoginTimeSeries from '../charts/LiveLoginTimeSeries'

import styles from './AppAnalytics.module.scss'
import { getGeneralStatsData } from '../../../api/Analytics'
import { roundTo } from '../../../utils/math'

class AppAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      statsData: undefined
    }
  }

  componentDidMount = () => {
    this.getGeneralStatsAnalytics()
  }

  getGeneralStatsAnalytics = () => {
    getGeneralStatsData().then((res) => {
      this.setState({ statsData: res.data })
    })
      .catch((err) => logError(
          err.toString(),
          err.message,
          'UsersAnalytics.getGeneralStatsAnalytics',
          err.stack
      ))
  }

  render() {

    const { statsData } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - Arclytics SimCCT</h3>

        <h5>Interesting numbers about the application</h5>
        <div className={styles.generalData}>

          <Card className={styles.generalDataCard}>
            <PlayCircleIcon color={getColor('--arc500')} size={36} />
            <h5>{(statsData !== undefined) ? statsData.count.simulations : "0"}</h5>
            <p>Run simulation</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <DatabaseIcon color={getColor('--arc500')} size={36} />
            <h5>{(statsData !== undefined) ? statsData.count.global_alloys : "0"}</h5>
            <p>Global alloys</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <StarIcon color={getColor('--arc500')} size={36} />
            <h5>{
              (statsData !== undefined) ? roundTo(parseFloat(statsData.average.ratings), 2) : "0"
            }
            </h5>
            <p>Ratings</p>
          </Card>


        </div>

        <h5>Users currently logged in</h5>
        <div className={styles.chart}>
          <Card className={styles.liveLoginCard}>
            {/*<div className={styles.liveLoginChart}>*/}
              <LiveLoginTimeSeries />
            {/*</div>*/}
          </Card>
        </div>
      </div>
    )
  }
}

// UsersAnalytics.propTypes = {}

export default AppAnalytics
