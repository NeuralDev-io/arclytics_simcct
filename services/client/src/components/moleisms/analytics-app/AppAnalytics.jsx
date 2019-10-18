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
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDatabase } from '@fortawesome/pro-light-svg-icons/faDatabase'
import { faPlayCircle } from '@fortawesome/pro-light-svg-icons/faPlayCircle'
import { faStar } from '@fortawesome/pro-light-svg-icons/faStar'
import { faCode } from '@fortawesome/pro-light-svg-icons/faCode'
import { logError } from '../../../api/LoggingHelper'
import { getColor } from '../../../utils/theming'
import Card from '../../elements/card'
import LiveLoginTimeSeries from '../charts/LiveLoginTimeSeries'

import styles from './AppAnalytics.module.scss'
import { getGeneralStatsData } from '../../../api/Analytics'
import { roundTo } from '../../../utils/math'

/*
* TODO (andrew@neuraldev.io):
*  - Li98 vs. Kirkaldy83 Bar plot.
*  - Alloys MDS plotting
*  - Ask Dr. Bendeich/Muransky if they have anything else they want.
*
* */

class AppAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      statsData: undefined,
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
        err.stack,
      ))
  }

  render() {
    const { statsData } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - Arclytics SimCCT</h3>

        <h5>Summary numbers about the application</h5>
        <div className={styles.generalData}>

          <Card className={styles.generalDataCard}>
            <FontAwesomeIcon icon={faPlayCircle} color={getColor('--arc500')}  className={styles.cardIcon} />
            <h5>{(statsData !== undefined) ? statsData.count.simulations : '0'}</h5>
            <p>Run simulation</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <FontAwesomeIcon icon={faDatabase}color={getColor('--arc500')} className={styles.cardIcon} />
            <h5>{(statsData !== undefined) ? statsData.count.global_alloys : '0'}</h5>
            <p>Global alloys</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <FontAwesomeIcon icon={faStar} color={getColor('--arc500')} className={styles.cardIcon} />
            <h5>
              {
                (statsData !== undefined) ? roundTo(parseFloat(statsData.average.ratings), 2) : '0'
              }
            </h5>
            <p>Average ratings</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <FontAwesomeIcon icon={faCode} color={getColor('--arc500')} className={styles.cardIcon} />
            <h5>0</h5>
            <p>More stuff</p>
          </Card>

        </div>

        <h5>Users currently logged in</h5>
        <div className={styles.chart}>
          <Card className={styles.liveLoginCard}>
            <LiveLoginTimeSeries />
          </Card>
        </div>
      </div>
    )
  }
}

export default AppAnalytics
