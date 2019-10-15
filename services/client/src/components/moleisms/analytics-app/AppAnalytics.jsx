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

import styles from './AppAnalytics.module.scss'

class AppAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      statsData: undefined,
      profileData: undefined,
      mapboxToken: '',
      mapboxData: undefined,
    }
  }

  componentDidMount = () => {}

  render() {

    const {
      statsData,
      profileData,
      mapboxToken,
      mapboxData,
    } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - Arclytics SimCCT</h3>

        <h5>Interesting numbers about the application</h5>
        <div className={styles.generalData}>

          <Card className={styles.generalDataCard}>
            <p>Run simulation</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <p>Global alloys</p>
          </Card>

          <Card className={styles.generalDataCard}>
            <p>Ratings</p>
          </Card>


        </div>

        <h5>Users currently logged in</h5>
        <div className={styles.charts}>

          <Card className={styles.liveLoginCard}>
            {/*<ProfileBarChart*/}
            {/*  title="Aim"*/}
            {/*  name="Aim"*/}
            {/*  data={(profileData !== undefined) ? profileData.aim : undefined}*/}
            {/*  color="--b500"*/}
            {/*/>*/}
          </Card>
        </div>
      </div>
    )
  }
}

// UsersAnalytics.propTypes = {}

export default AppAnalytics
