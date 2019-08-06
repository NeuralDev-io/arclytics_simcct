import React, { Component } from 'react'
import ActivityIcon from 'react-feather/dist/icons/activity'
import DatabaseIcon from 'react-feather/dist/icons/database'
import UsersIcon from 'react-feather/dist/icons/users'

import styles from './AdminSidebar.module.scss'

class AdminSidebar extends Component {
  constructor(props) {
    super(props)
    this.state = {
      active: 'analytics',
    }
  }

  render() {
    const { active } = this.state
    return (
      <div className={styles.sidebar}>
        <h4>Dashboard</h4>
        <a
          id="analytics"
          href="/admin/analytics"
          className={`${styles.item} ${active === 'analytics' && styles.active}`}
        >
          <ActivityIcon className={styles.icon} />
          <h6>Analytics</h6>
        </a>
        <a
          id="alloys"
          href="/admin/alloys"
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <DatabaseIcon className={styles.icon} />
          <h6>Alloy database</h6>
        </a>
        <a
          id="users"
          href="/admin/users"
          className={`${styles.item} ${active === 'users' && styles.active}`}
        >
          <UsersIcon className={styles.icon} />
          <h6>Manage users</h6>
        </a>
      </div>
    )
  }
}

export default AdminSidebar
