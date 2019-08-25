import React, { Component } from 'react'
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
        <a
          id="analytics"
          href="/admin/analytics"
          className={`${styles.item} ${active === 'analytics' && styles.active}`}
        >
          <ActivityIcon className={styles.icon} />
          <span>Analytics</span>
        </a>
        <a
          id="alloys"
          href="/admin/alloys"
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <DatabaseIcon className={styles.icon} />
          <span>Alloy database</span>
        </a>
        <a
          id="users"
          href="/admin/users"
          className={`${styles.item} ${active === 'users' && styles.active}`}
        >
          <UsersIcon className={styles.icon} />
          <span>Manage users</span>
        </a>
      </div>
    )
  }
}

export default AdminSidebar