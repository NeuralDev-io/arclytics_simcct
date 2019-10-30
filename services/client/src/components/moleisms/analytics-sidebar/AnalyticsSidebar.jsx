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
import { Link, withRouter } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faServer } from '@fortawesome/pro-light-svg-icons/faServer'
import { faUserFriends } from '@fortawesome/pro-light-svg-icons/faUserFriends'
import { faAtomAlt } from '@fortawesome/pro-light-svg-icons/faAtomAlt'
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
    if (!['app', 'users', 'simulations'].includes(active)) {
      this.setState({ active: 'users' })
      redirect('/analytics/users')
    }
  }

  componentDidUpdate = (prevProps) => {
    const { location } = this.props
    if (prevProps.location !== location) {
      const pathArr = location.pathname.split('/')
      this.setState({
        active: pathArr[pathArr.length - 1],
      })
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
          className={`${styles.item} ${active === 'users' && styles.active}`}
        >
          <FontAwesomeIcon icon={faUserFriends} className={styles.icon} size="lg" />
          <span>Users</span>
        </Link>

        <Link
          id="simulations"
          to="/analytics/simulations"
          className={`${styles.item} ${active === 'simulations' && styles.active}`}
        >
          <FontAwesomeIcon icon={faAtomAlt} className={styles.icon} size="lg" />
          <span>Simulations</span>
        </Link>

        <Link
          id="application"
          to="/analytics/app"
          className={`${styles.item} ${active === 'app' && styles.active}`}
        >
          <FontAwesomeIcon icon={faServer} className={styles.icon} size="lg" />
          <span>Application</span>
        </Link>

      </div>
    )
  }
}

AnalyticsSidebar.propTypes = {
  redirect: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string,
  }).isRequired,
}

export default withRouter(AnalyticsSidebar)
