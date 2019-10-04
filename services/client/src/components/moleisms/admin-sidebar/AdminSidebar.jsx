/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
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
