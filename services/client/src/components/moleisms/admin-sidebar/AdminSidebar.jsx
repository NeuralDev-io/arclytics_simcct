/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Admin sidebar
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link, withRouter } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDatabase } from '@fortawesome/pro-light-svg-icons/faDatabase'
import { faUserFriends } from '@fortawesome/pro-light-svg-icons/faUserFriends'

import styles from './AdminSidebar.module.scss'

class AdminSidebar extends Component {
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
    if (!['alloys', 'users'].includes(active)) {
      this.setState({ active: 'alloys' })
      redirect('/admin/alloys')
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
        <h4>Dashboard</h4>
        <Link
          id="alloys"
          to="/admin/alloys"
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <FontAwesomeIcon icon={faDatabase} className={styles.icon} />
          <span>Alloy database</span>
        </Link>
        <Link
          id="users"
          to="/admin/users"
          className={`${styles.item} ${active === 'users' && styles.active}`}
        >
          <FontAwesomeIcon icon={faUserFriends} className={styles.icon} />
          <span>Manage users</span>
        </Link>
      </div>
    )
  }
}

AdminSidebar.propTypes = {
  redirect: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string,
  }).isRequired,
}

export default withRouter(AdminSidebar)
