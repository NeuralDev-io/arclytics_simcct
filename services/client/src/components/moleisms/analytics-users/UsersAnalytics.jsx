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
import { getProfileAnalyticsData } from '../../../api/Analytics'
import { logError, logInfo } from '../../../api/LoggingHelper'
import ProfileBarChart from '../charts/ProfileBarChart'
import Card from '../../elements/card'

import styles from './UsersAnalytics.module.scss'

/*
  * This is what the returned data looks like.
  *
  * 'plotly_chart_type': 'bar',
  * 'data': {
  *     'aim': {
  *         'x': list(df['aim'].unique()),
  *         'y': list(df['aim'].value_counts())
  *     },
  *     'highest_education': {
  *         'x': list(df['highest_education'].unique()),
  *         'y': list(df['highest_education'].value_counts())
  *     },
  *     'sci_tech_exp': {
  *         'x': list(df['sci_tech_exp'].unique()),
  *         'y': list(df['sci_tech_exp'].value_counts())
  *     },
  *     'phase_transform_exp': {
  *         'x': list(df['phase_transform_exp'].unique()),
  *         'y': list(df['phase_transform_exp'].value_counts())
  *     }
  * }
  * */

class UsersAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {
      data: undefined
    }
  }

  componentDidMount = () => {
    this.getProfileAnalytics()
  }

  getProfileAnalytics = () => {
    getProfileAnalyticsData().then((res) => {
      this.setState({ data: res.data })
    })
      .catch((err) => logError(
        err.toString(),
        err.message,
        'UsersAnalytics.getProfileAnalytics',
        err.stack
      ))
  }

  render() {

    const { data } = this.state

    /*
    * Colors: --l300, --g300, --m300, --r300, --o300
    * */

    return (
      <div className={styles.container}>
        <h3>All About Users</h3>

        <h5>Live Logged In Users</h5>
        <br/><br/>

        <h5>Users Profiles</h5>

        <div className={styles.charts}>

          <Card>
            <ProfileBarChart
              title="Aim"
              name="Aim"
              data={(data !== undefined) ? data.aim : undefined}
              color="--b500"
            />
          </Card>

          <Card>
            <ProfileBarChart
              title="Highest Education"
              name="Highest Education"
              data={(data !== undefined) ? data.highest_education : undefined}
              color="--o500"
            />
          </Card>

          <Card>
            <ProfileBarChart
            title="Scientific Software Experience"
            name="Scientific Software Experience"
            data={(data !== undefined) ? data.sci_tech_exp : undefined}
            color="--g500"
          />
          </Card>

          <Card>
            <ProfileBarChart
              title="Phase Transformation Experience"
              name="Phase Transformation Experience"
              data={(data !== undefined) ? data.phase_transform_exp : undefined}
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
