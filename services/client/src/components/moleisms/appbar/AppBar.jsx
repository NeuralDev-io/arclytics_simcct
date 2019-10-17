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
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOut } from '@fortawesome/pro-light-svg-icons/faSignOut'
import { faUser } from '@fortawesome/pro-light-svg-icons/faUser'
import { faAnalytics } from '@fortawesome/pro-light-svg-icons/faAnalytics'
import { faQuestionCircle } from '@fortawesome/pro-light-svg-icons'
import { faUserCog } from '@fortawesome/pro-light-svg-icons/faUserCog'
// import HelpIcon from 'react-feather/dist/icons/help-circle'
import { faSlidersV } from '@fortawesome/pro-light-svg-icons/faSlidersV'
import { faDatabase } from '@fortawesome/pro-light-svg-icons/faDatabase'
import { ReactComponent as SimulationIcon } from '../../../assets/simulation icon.svg'
import { faFileChartLine } from '@fortawesome/pro-light-svg-icons/faFileChartLine'
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
              {/*<SlidersIcon className={styles.icon} />*/}
              <SimulationIcon className={styles.icon}/>
              <p>Simulation</p>
            </Tooltip>
          </Link>
          <Link
            id="equilibrium"
            className={`${styles.navIcon} ${active === 'equilibrium' && styles.active}`}
            to="/equilibrium"
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <FontAwesomeIcon icon={faSlidersV} className={styles.icon} size="lg" />
              <p>Equilibrium</p>
            </Tooltip>
          </Link>
          <Link
            id="savedSimulations"
            className={`${styles.navIcon} ${active === 'savedSimulations' && styles.active} ${!isAuthenticated && styles.disabled}`}
            to={isAuthenticated ? '/user/simulations' : ''}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              {/*<HardDriveIcon className={styles.icon} />*/}
              <FontAwesomeIcon icon={faFileChartLine} className={styles.icon} size="lg" />
              <p>Saved simulations</p>
            </Tooltip>
          </Link>
          <Link
            id="alloys"
            className={`${styles.navIcon} ${active === 'userAlloys' && styles.active} ${!isAuthenticated && styles.disabled}`}
            to={isAuthenticated ? '/user/alloys' : ''}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <FontAwesomeIcon icon={faDatabase} className={styles.icon} size="lg" />
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
            className={`${styles.navIcon} ${active === 'analytiActivityIconcs' && styles.active}`}
            style={{ display: isAdmin ? 'flex' : 'none' }}
            to="/analytics/users"
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <FontAwesomeIcon icon={faAnalytics} className={styles.icon} size="lg" />
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
              <FontAwesomeIcon icon={faUserCog} className={styles.icon} size="lg" />
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
              <FontAwesomeIcon icon={faUser} className={styles.icon} size="lg" />
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
              <FontAwesomeIcon icon={faSignOut} className={styles.icon} size="lg" />
              <p>Logout</p>
            </Tooltip>
          </div>

          <div
            id="about"
            className={`${styles.navIcon} ${!isAuthenticated && styles.disabled}`}
            {...(() => {
              if (isAuthenticated) return buttonize(this.handleLogout)
              return {}
            })()}
          >
            <Tooltip className={{ tooltip: styles.tooltip }} position="right">
              <FontAwesomeIcon icon={faQuestionCircle} className={styles.icon} size="lg" />
              <p>About</p>
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
