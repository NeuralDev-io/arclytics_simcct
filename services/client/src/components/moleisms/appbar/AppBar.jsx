import React from 'react'
import PropTypes from 'prop-types'
import ActivityIcon from 'react-feather/dist/icons/activity'
import HelpIcon from 'react-feather/dist/icons/help-circle'
import UserIcon from 'react-feather/dist/icons/user'
import LogOutIcon from 'react-feather/dist/icons/log-out'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { logout } from '../../../utils/AuthenticationHelper'

import styles from './AppBar.module.scss'

const AppBar = (props) => {
  const { active, redirect } = props
  return (
    <nav className={styles.navContainer}>
      <div>
        <Logo className={styles.logo} />
        <ActivityIcon className={`${styles.navIcon} ${active === 'sim' && styles.active}`} />
        <HelpIcon className={`${styles.navIcon} ${active === 'edu' && styles.active}`} />
      </div>
      <div>
        <UserIcon 
          className={`${styles.navIcon} ${active === 'user' && styles.active}`}
          onClick={() => {
            redirect('/profile')
          }}
        />
        <LogOutIcon
          className={styles.navIcon}
          onClick={() => {
            logout()
            localStorage.removeItem('token')
            redirect('/signin')
          }}
        />
      </div>
    </nav>
  )
}

AppBar.propTypes = {
  active: PropTypes.string.isRequired,
  redirect: PropTypes.func.isRequired,
}

export default AppBar
