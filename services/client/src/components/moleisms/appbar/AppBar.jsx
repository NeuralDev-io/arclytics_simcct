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
import { ReactComponent as AnstoLogo } from '../../../assets/ANSTO_Logo_SVG/logo.svg'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import Tooltip from '../../elements/tooltip'
import { logout } from '../../../utils/AuthenticationHelper'
import { buttonize } from '../../../utils/accessibility'

import styles from './AppBar.module.scss'

const AppBar = (props) => {
  const { active, redirect, user } = props
  return (
    <nav className={styles.navContainer}>
      <div>
        <AnstoLogo className={styles.logo} />
        <a
          id="sim"
          className={`${styles.navIcon} ${active === 'sim' && styles.active}`}
          href="/"
        >
          <Tooltip className={styles.tooltip} position="right">
            <SlidersIcon className={styles.icon} />
            <p> Simulation </p>
          </Tooltip>
        </a>
        <a
          id="savedSimulations"
          className={`${styles.navIcon} ${active === 'savedSimulations' && styles.active}`}
          href="/user/simulations"
        >
          <Tooltip className={styles.tooltip} position="right">
            <HardDriveIcon className={styles.icon} />
            <p> Saved simulations </p>
          </Tooltip>
        </a>
        <a
          id="alloys"
          className={`${styles.navIcon} ${active === 'userAlloys' && styles.active}`}
          href="/user/alloys"
        >
          <Tooltip className={styles.tooltip} position="right">
            <DatabaseIcon className={styles.icon} />
            <p> Alloy database </p>
          </Tooltip>
        </a>
        <a
          id="help"
          className={`${styles.navIcon} ${active === 'edu' && styles.active}`}
          href="/"
        >
          <Tooltip className={styles.tooltip} position="right">
            <HelpIcon className={styles.icon} />
            <p> Help </p>
          </Tooltip>
        </a>
        <a
          id="admin"
          className={`${styles.navIcon} ${active === 'admin' && styles.active}`}
          style={{ display: user.admin ? 'flex' : 'none' }}
          href="/admin/analytics"
        >
          <Tooltip className={styles.tooltip} position="right">
            <MonitorIcon className={styles.icon} />
            <p> Admin </p>
          </Tooltip>
        </a>
      </div>
      <div>
        <a
          id="profile"
          className={`${styles.navIcon} ${active === 'profile' && styles.active}`}
          href="/user/profile"
        >
          <Tooltip className={styles.tooltip} position="right">
            <UserIcon className={styles.icon} />
            <p> Profile </p>
          </Tooltip>
        </a>
        <div
          id="logout"
          className={styles.navIcon}
          {...buttonize(() => logout(redirect))}
        >
          <Tooltip className={styles.tooltip} position="right">
            <LogOutIcon className={styles.icon} />
            <p> Logout </p>
          </Tooltip>
          
        </div>
        <Logo className={styles.logo} />
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
