import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import ActivityIcon from 'react-feather/dist/icons/activity'
import DatabaseIcon from 'react-feather/dist/icons/database'
import UsersIcon from 'react-feather/dist/icons/users'

import styles from './AdminSidebar.module.scss'

class AdminSidebar extends Component {
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
        <h4>Dashboard</h4>
        <Link
          id="analytics"
          to="/admin/analytics"
          onClick={() => this.setState({ active: 'analytics' })}
          className={`${styles.item} ${active === 'analytics' && styles.active}`}
        >
          <ActivityIcon className={styles.icon} />
          <span>Analytics</span>
        </Link>
        <Link
          id="alloys"
          to="/admin/alloys"
          onClick={() => this.setState({ active: 'alloys' })}
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <DatabaseIcon className={styles.icon} />
          <span>Alloy database</span>
        </Link>
        <Link
          id="users"
          to="/admin/users"
          onClick={() => this.setState({ active: 'users' })}
          className={`${styles.item} ${active === 'users' && styles.active}`}
        >
          <UsersIcon className={styles.icon} />
          <span>Manage users</span>
        </Link>
      </div>
    )
  }
}

export default AdminSidebar
