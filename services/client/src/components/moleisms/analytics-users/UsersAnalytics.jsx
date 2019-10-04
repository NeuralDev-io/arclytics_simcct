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
import ProfileBarChart from '../charts/ProfileBarChart'

import styles from './UsersAnalytics.module.scss'

class UsersAnalytics extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  componentDidMount = () => {}

  render() {
    return (
      <div className={styles.container}>
        <h3>All About Users</h3>

        <h5>Live Logged In Users</h5>
        <br/><br/>

        <h5>Users Profiles</h5>

        <div>
          <ProfileBarChart />
        </div>

        <br/><br/>

      </div>
    )
  }
}

UsersAnalytics.propTypes = {}

export default UsersAnalytics
