/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Analytics specific to Users data.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { getProfileAnalyticsData, getLoginLocationData } from '../../../api/Analytics'
import { logError, logInfo } from '../../../api/LoggingHelper'
import { ProfileBarChart, LoginLocationMapbox } from '../charts'
import Card from '../../elements/card'

import styles from './UsersAnalytics.module.scss'

class UsersAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      profileData: undefined,
      mapboxToken: '',
      mapboxData: undefined,
    }
  }

  componentDidMount = () => {
    this.getProfileAnalytics()
    this.getLoginLocationMap()
  }

  getProfileAnalytics = () => {
    getProfileAnalyticsData().then((res) => {
      this.setState({ profileData: res.data })
    })
      .catch((err) => logError(
        err.toString(),
        err.message,
        'UsersAnalytics.getProfileAnalytics',
        err.stack
      ))
  }

  getLoginLocationMap = () => {
    getLoginLocationData().then((res) => {
      // noinspection JSUnresolvedVariable
      this.setState({
        mapboxData: res.data,
        mapboxToken: res.mapbox_token
      })
    })
      .catch((err) => logError(
        err.toString(),
        err.message,
        'UsersAnalytics.getProfileAnalytics',
        err.stack
      ))
  }

  render() {

    const {
      profileData,
      mapboxToken,
      mapboxData,
    } = this.state

    /*
    * Colors: --l300, --g300, --m300, --r300, --o300
    * */

    return (
      <div className={styles.container}>
        <h3>Dashboard - All About Users</h3>

        <h5>Some <strike>nerdy stats</strike> numbers about users.</h5>
        <div className={styles.liveData}>
          <Card className={styles.liveDataCard}>

          </Card>
        </div>

        <h5>Where are users located?</h5>
        <div className={styles.map}>
          <Card className={styles.mapCard}>
            <LoginLocationMapbox
              token={mapboxToken}
              data={(mapboxData !== undefined) ? mapboxData : undefined}
            />
          </Card>
        </div>

        <h5>What do users say about themselves?</h5>
        <div className={styles.charts}>

          <Card className={styles.profileCard}>
            <ProfileBarChart
              title="Aim"
              name="Aim"
              data={(profileData !== undefined) ? profileData.aim : undefined}
              color="--b500"
            />
          </Card>

          <Card className={styles.profileCard}>
            <ProfileBarChart
              title="Highest Education"
              name="Highest Education"
              data={(profileData !== undefined) ? profileData.highest_education : undefined}
              color="--o500"
            />
          </Card>

          <Card className={styles.profileCard}>
            <ProfileBarChart
            title="Scientific Software Experience"
            name="Scientific Software Experience"
            data={(profileData !== undefined) ? profileData.sci_tech_exp : undefined}
            color="--g500"
          />
          </Card>

          <Card className={styles.profileCard}>
            <ProfileBarChart
              title="Phase Transformation Experience"
              name="Phase Transformation Experience"
              data={(profileData !== undefined) ? profileData.phase_transform_exp : undefined}
              color="--r500"
            />
          </Card>

        </div>
      </div>
    )
  }
}

// UsersAnalytics.propTypes = {}

export default UsersAnalytics
