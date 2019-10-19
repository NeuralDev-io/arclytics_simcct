/**
 *
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
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faServer } from '@fortawesome/pro-light-svg-icons/faServer'
import { faUserFriends } from '@fortawesome/pro-light-svg-icons/faUserFriends'
import styles from './AnalyticsSidebar.module.scss'

class AnalyticsSidebar extends Component {
  constructor(props) {
    super(props)
    const pathArr = window.location.pathname.split('/')
    this.state = {
      active: pathArr[pathArr.length - 1],
    }
  }

  componentDidMount = () => {
    const { active } = this.state
    const { redirect } = this.props
    if (!['application', 'users'].includes(active)) {
      this.setState({ active: 'application' })
      redirect('/analytics/app')
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
          <FontAwesomeIcon icon={faUserFriends} className={styles.icon} size="lg"/>
          <span>Users</span>
        </Link>

        {/* <Link */}
        {/*  id="alloys" */}
        {/*  to="/analytics/alloys" */}
        {/*  onClick={() => this.setState({ active: 'alloys' })} */}
        {/*  className={`${styles.item} ${active === 'alloys' && styles.active}`} */}
        {/* > */}
        {/*  <DatabaseIcon className={styles.icon} /> */}
        {/*  <span>Alloys</span> */}
        {/* </Link> */}

        <Link
          id="application"
          to="/analytics/app"
          onClick={() => this.setState({ active: 'application' })}
          className={`${styles.item} ${active === 'application' && styles.active}`}
        >
          <FontAwesomeIcon icon={faServer} className={styles.icon} size="lg"/>
          <span>Application</span>
        </Link>

      </div>
    )
  }
}

AnalyticsSidebar.propTypes = {
  redirect: PropTypes.func.isRequired,
}

export default AnalyticsSidebar
