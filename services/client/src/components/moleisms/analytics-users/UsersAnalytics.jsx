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
import UsersIcon from 'react-feather/dist/icons/users'
import DatabaseIcon from 'react-feather/dist/icons/database'
import Share2Icon from 'react-feather/dist/icons/share-2'
import SaveIcon from 'react-feather/dist/icons/save'
import HeartIcon from 'react-feather/dist/icons/heart'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUserFriends } from '@fortawesome/pro-light-svg-icons/faUserFriends'
import { faDatabase } from '@fortawesome/pro-light-svg-icons/faDatabase'
import { faSave } from '@fortawesome/pro-light-svg-icons/faSave'
import { faShareAlt } from '@fortawesome/pro-light-svg-icons/faShareAlt'
import { faHeart } from '@fortawesome/pro-light-svg-icons/faHeart'
import {
  getProfileAnalyticsData,
  getLoginLocationData,
  getNerdyStatsData
} from '../../../api/Analytics'
import { logError, logInfo } from '../../../api/LoggingHelper'
import { ProfileBarChart, LoginLocationMapbox } from '../charts'
import { getColor } from '../../../utils/theming'
import Card from '../../elements/card'

import styles from './UsersAnalytics.module.scss'

const colorScale = [
  // Let first 10% (0.1) of the values have color rgb(0, 0, 0)
  [0, 'rgb(0, 0, 0)'],
  [0.1, 'rgb(0, 0, 0)'],
  // Let values between 10-20% of the min and max of z have color rgb(20, 20, 20)
  [0.1, 'rgb(20, 20, 20)'],
  [0.2, 'rgb(20, 20, 20)'],
  // Values between 20-30% of the min and max of z have color rgb(40, 40, 40)
  [0.2, 'rgb(40, 40, 40)'],
  [0.3, 'rgb(40, 40, 40)'],

  [0.3, 'rgb(60, 60, 60)'],
  [0.4, 'rgb(60, 60, 60)'],

  [0.4, 'rgb(80, 80, 80)'],
  [0.5, 'rgb(80, 80, 80)'],

  [0.5, 'rgb(100, 100, 100)'],
  [0.6, 'rgb(100, 100, 100)'],

  [0.6, 'rgb(120, 120, 120)'],
  [0.7, 'rgb(120, 120, 120)'],

  [0.7, 'rgb(140, 140, 140)'],
  [0.8, 'rgb(140, 140, 140)'],

  [0.8, 'rgb(160, 160, 160)'],
  [0.9, 'rgb(160, 160, 160)'],

  [0.9, 'rgb(180, 180, 180)'],
  [1.0, 'rgb(180, 180, 180)']
]

class UsersAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      statsData: undefined,
      profileData: undefined,
      mapboxToken: '',
      mapboxData: undefined,
    }
  }

  componentDidMount = () => {
    this.getNerdyStatsAnalytics()
    this.getProfileAnalytics()
    this.getLoginLocationMap()
  }

  getNerdyStatsAnalytics = () => {
    getNerdyStatsData().then((res) => {
      this.setState({ statsData: res.data })
    })
      .catch((err) => logError(
          err.toString(),
          err.message,
          'UsersAnalytics.getNerdyStatsAnalytics',
          err.stack
      ))
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
      statsData,
      profileData,
      mapboxToken,
      mapboxData,
    } = this.state

    return (
      <div className={styles.container}>
        <h3>Dashboard - All About Users</h3>

        <h5>Some <strike>nerdy stats</strike> numbers about users.</h5>
        <div className={styles.nerdyData}>
          <Card className={styles.nerdyDataCard}>

            <div className={styles.nerdyDataItem}>
              <FontAwesomeIcon icon={faUserFriends} color={getColor('--r400')} className={styles.cardIcon} />
              <h5>{(statsData !== undefined) ? statsData.count.users : "0"}</h5>
              <p>Users</p>
            </div>

            <div className={styles.nerdyDataItem}>
              <FontAwesomeIcon icon={faDatabase} color={getColor('--o400')} className={styles.cardIcon} />
              <h5>{(statsData !== undefined) ? statsData.count.saved_alloys : "0"}</h5>
              <p>Saved Alloys</p>
            </div>

            <div className={styles.nerdyDataItem}>
              <FontAwesomeIcon icon={faSave} color={getColor('--t400')} className={styles.cardIcon} />
              <h5>{(statsData !== undefined) ? statsData.count.saved_simulations : "0"}</h5>
              <p>Saved Simulations</p>
            </div>

            <div className={styles.nerdyDataItem}>
              <FontAwesomeIcon icon={faShareAlt} color={getColor('--b400')} className={styles.cardIcon} />
              <h5>{(statsData !== undefined) ? statsData.count.shared_simulations : "0"}</h5>
              <p>Shared Simulations</p>
            </div>

            <div className={styles.nerdyDataItem}>
              <FontAwesomeIcon icon={faHeart} color={getColor('--i400')} className={styles.cardIcon} />
              <h5>{(statsData !== undefined) ? statsData.count.feedback : "0"}</h5>
              <p>Feedback</p>
            </div>

          </Card>
        </div>

        <h5>Where are users located?</h5>
        <div className={styles.map}>
          <Card className={styles.mapCard}>
            {/*
              * TODO(andrew@neuraldev.io): The custom colorScale is not working.
              *  It seems to delete on re-render for some reason.
              *
            */ }
            <LoginLocationMapbox
              // Other options include: Electric, Viridis, Hot, Jet, YIGnBu, YIOrRd, Picnic
              colorScale={(mapboxData !== undefined) ? 'YIGnBu' : colorScale}
              mapBoxStyle={'light'}  // Can also pass in 'dark' for dark mode.
              token={mapboxToken}
              data={(mapboxData !== undefined) ? mapboxData : undefined}
            />
          </Card>
        </div>

        <h5>What do users say about themselves?</h5>
        <div className={styles.profileCharts}>

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
