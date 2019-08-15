import React, { Component } from 'react'
import UserIcon from 'react-feather/dist/icons/user'
import DatabaseIcon from 'react-feather/dist/icons/database'
import SlidersIcon from 'react-feather/dist/icons/sliders'

import styles from './UserSidebar.module.scss'

class UserSidebar extends Component {
  constructor(props) {
    super(props)
    // We get the URL from the current window object and split on '/'
    const pathArr = window.location.pathname.split('/')

    this.state = {
      // Get the last element which is basically the same ID name in the below defined
      // navigation links to set the className style on it to make it `active`
      active: pathArr[pathArr.length - 1],
    }
  }

  render() {
    const { active } = this.state
    return (
      <div className={styles.sidebar}>
        <h4>User</h4>
        <a
          id="profile"
          href="/user/profile"
          className={`${styles.item} ${active === 'profile' && styles.active}`}
        >
          <UserIcon className={styles.icon} />
          <span>Profile</span>
        </a>
        <a
          id="alloy"
          href="/user/alloys"
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <DatabaseIcon className={styles.icon} />
          <span>Alloy database</span>
        </a>
        <a
          id="simulations"
          href="/user/simulations"
          className={`${styles.item} ${active === 'simulations' && styles.active}`}
        >
          <SlidersIcon className={styles.icon} />
          <span>Saved simulations</span>
        </a>
      </div>
    )
  }
}

export default UserSidebar
