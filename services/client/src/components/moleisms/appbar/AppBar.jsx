/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Appbar component
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import ActivityIcon from 'react-feather/dist/icons/activity'
import HardDriveIcon from 'react-feather/dist/icons/hard-drive'
// import HelpIcon from 'react-feather/dist/icons/help-circle'
import MonitorIcon from 'react-feather/dist/icons/monitor'
import UserIcon from 'react-feather/dist/icons/user'
import LogOutIcon from 'react-feather/dist/icons/log-out'
import DatabaseIcon from 'react-feather/dist/icons/database'
import SlidersIcon from 'react-feather/dist/icons/sliders'
import { ReactComponent as ANSTOLogo } from '../../../assets/ANSTO_Logo_SVG/logo.svg'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import Tooltip from '../../elements/tooltip'
import store from '../../../state/store'
import { logout } from '../../../api/AuthenticationHelper'
import { buttonize } from '../../../utils/accessibility'
import { saveLastSim } from '../../../state/ducks/self/actions'
import { addFlashToast } from '../../../state/ducks/toast/actions'
import { logError } from '../../../api/LoggingHelper'

import styles from './AppBar.module.scss'

class AppBar extends React.Component {
  handleLogout = async () => {
    const { addFlashToastConnect, saveLastSimConnect, redirect } = this.props
    await saveLastSimConnect()
    logout()
      .then(() => {
        redirect('/signin')
        store.dispatch({ type: 'USER_LOGOUT' })
      })
      .catch((err) => {
        logError(err.toString(), err.messages, 'AppBar.handleLogout', err.stack_trace)
        addFlashToastConnect({
          message: 'We couldn\'t log you out. Please try again',
          options: { variant: 'error' },
        }, true)
      })
  }

  render() {
    const {
      active,
      isAdmin,
      isAuthenticated,
    } = this.props

    return (
      <nav className={styles.navContainer}>
        <div>
          <ANSTOLogo className={styles.anstoLogo} />
          <Link
            id="sim"
            className={`${styles.navIcon} ${active === 'sim' && styles.active}`}
            to="/"
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <SlidersIcon className={styles.icon} />
              <p>Simulation</p>
            </Tooltip>
          </Link>
          <Link
            id="savedSimulations"
            className={`${styles.navIcon} ${active === 'savedSimulations' && styles.active} ${!isAuthenticated && styles.disabled}`}
            to={isAuthenticated ? '/user/simulations' : ''}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <HardDriveIcon className={styles.icon} />
              <p>Saved simulations</p>
            </Tooltip>
          </Link>
          <Link
            id="alloys"
            className={`${styles.navIcon} ${active === 'userAlloys' && styles.active} ${!isAuthenticated && styles.disabled}`}
            to={isAuthenticated ? '/user/alloys' : ''}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <DatabaseIcon className={styles.icon} />
              <p>Alloy database</p>
            </Tooltip>
          </Link>
          {/* <a
            id="help"
            className={`${styles.navIcon} ${active === 'edu' && styles.active}
            ${!isAuthenticated && styles.disabled}`}
            href={isAuthenticated ? '/' : ''}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <HelpIcon className={styles.icon} />
              <p>Help</p>
            </Tooltip>
          </a> */}

          <div
            className={styles.line}
            style={{ display: isAdmin ? 'flex' : 'none' }}
          />

          <Link
            id="analytics"
            className={`${styles.navIcon} ${active === 'analytics' && styles.active}`}
            style={{ display: isAdmin ? 'flex' : 'none' }}
            to="/analytics/users"
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <ActivityIcon className={styles.icon} />
              <p>Data & Analytics</p>
            </Tooltip>
          </Link>

          <Link
            id="admin"
            className={`${styles.navIcon} ${active === 'admin' && styles.active}`}
            style={{ display: isAdmin ? 'flex' : 'none' }}
            to="/admin/analytics"
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <MonitorIcon className={styles.icon} />
              <p>Admin</p>
            </Tooltip>
          </Link>
        </div>
        <div>
          <Link
            id="profile"
            className={`${styles.navIcon} ${active === 'user' && styles.active} ${!isAuthenticated && styles.disabled}`}
            to={isAuthenticated ? '/user/profile' : ''}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <UserIcon className={styles.icon} />
              <p>Account</p>
            </Tooltip>
          </Link>
          <div
            id="logout"
            className={`${styles.navIcon} ${!isAuthenticated && styles.disabled}`}
            {...(() => {
              if (isAuthenticated) return buttonize(this.handleLogout)
              return {}
            })()}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <LogOutIcon className={styles.icon} />
              <p>Logout</p>
            </Tooltip>
          </div>
          <Logo className={styles.logo} />
        </div>
      </nav>
    )
  }
}

AppBar.propTypes = {
  active: PropTypes.string.isRequired,
  redirect: PropTypes.func.isRequired,
  isAdmin: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  // from connect
  addFlashToastConnect: PropTypes.func.isRequired,
  saveLastSimConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
  saveLastSimConnect: saveLastSim,
}

export default connect(null, mapDispatchToProps)(AppBar)
