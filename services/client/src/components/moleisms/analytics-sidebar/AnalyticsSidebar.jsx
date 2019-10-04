/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AnalyticsSidebar
 *
 * Sidebar for the Analytics page with different Analytics options.
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import ServerIcon from 'react-feather/dist/icons/server'
import DatabaseIcon from 'react-feather/dist/icons/database'
import UsersIcon from 'react-feather/dist/icons/users'

import styles from './AnalyticsSidebar.module.scss'

class AnalyticsSidebar extends Component {
  constructor(props) {
    super(props)
    const pathArr = window.location.pathname.split('/')
    this.state = {
      active: pathArr[pathArr.length - 1],
    }
  }

  render() {
    const { active } = this.state
    return (
      <div className={styles.sidebar}>
        <h4>Analytics</h4>

        <Link
          id="users"
          to="/analytics/users"
          onClick={() => this.setState({ active: 'users' })}
          className={`${styles.item} ${active === 'users' && styles.active}`}
        >
          <UsersIcon className={styles.icon} />
          <span>Users</span>
        </Link>

        <Link
          id="alloys"
          to="/analytics/alloys"
          onClick={() => this.setState({ active: 'alloys' })}
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <DatabaseIcon className={styles.icon} />
          <span>Alloys</span>
        </Link>

        <Link
          id="application"
          to="/analytics/app"
          onClick={() => this.setState({ active: 'application' })}
          className={`${styles.item} ${active === 'application' && styles.active}`}
        >
          <ServerIcon className={styles.icon} />
          <span>Application</span>
        </Link>

      </div>
    )
  }
}

export default AnalyticsSidebar
