import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import HardDriveIcon from 'react-feather/dist/icons/hard-drive'
import HelpIcon from 'react-feather/dist/icons/help-circle'
import MonitorIcon from 'react-feather/dist/icons/monitor'
import UserIcon from 'react-feather/dist/icons/user'
import LogOutIcon from 'react-feather/dist/icons/log-out'
import DatabaseIcon from 'react-feather/dist/icons/database'
import SlidersIcon from 'react-feather/dist/icons/sliders'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { logout } from '../../../utils/AuthenticationHelper'
import { buttonize } from '../../../utils/accessibility'

import styles from './AppBar.module.scss'

const AppBar = (props) => {
  const { active, redirect, user } = props
  return (
    <nav className={styles.navContainer}>
      <div>
        <Logo className={styles.logo} />
        <a
          id="sim"
          className={`${styles.navIcon} ${active === 'sim' && styles.active}`}
          href="/"
        >
          <SlidersIcon className={styles.icon} />
        </a>
        <a
          id="savedSimulations"
          className={`${styles.navIcon} ${active === 'savedSimulations' && styles.active}`}
          href="/user/simulations"
        >
          <HardDriveIcon className={styles.icon} />
        </a>
        <a
          id="alloys"
          className={`${styles.navIcon} ${active === 'alloys' && styles.active}`}
          href="/user/alloys"
        >
          <DatabaseIcon className={styles.icon} />
        </a>
        <a
          id="help"
          className={`${styles.navIcon} ${active === 'edu' && styles.active}`}
          href="/"
        >
          <HelpIcon className={styles.icon} />
        </a>
        <a
          id="admin"
          className={`${styles.navIcon} ${active === 'admin' && styles.active}`}
          style={{ display: user.admin ? 'flex' : 'none' }}
          href="/admin/analytics"
        >
          <MonitorIcon className={styles.icon} />
        </a>
      </div>
      <div>
        <a
          id="profile"
          className={`${styles.navIcon} ${active === 'profile' && styles.active}`}
          href="/user/profile"
        >
          <UserIcon className={styles.icon} />
        </a>
        <div
          id="logout"
          className={styles.navIcon}
          {...buttonize(() => logout(redirect))}
        >
          <LogOutIcon className={styles.icon} />
        </div>
      </div>
    </nav>
  )
}

AppBar.propTypes = {
  active: PropTypes.string.isRequired,
  redirect: PropTypes.func.isRequired,
  user: PropTypes.shape({ admin: PropTypes.bool.isRequired }).isRequired,
}

const mapStateToProps = state => ({
  user: state.persist.userStatus,
})

export default connect(mapStateToProps, {})(AppBar)
