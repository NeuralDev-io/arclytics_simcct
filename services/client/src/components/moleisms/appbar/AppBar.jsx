import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import ActivityIcon from 'react-feather/dist/icons/activity'
import HelpIcon from 'react-feather/dist/icons/help-circle'
import MonitorIcon from 'react-feather/dist/icons/monitor'
import UserIcon from 'react-feather/dist/icons/user'
import LogOutIcon from 'react-feather/dist/icons/log-out'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { logout } from '../../../utils/AuthenticationHelper'

import styles from './AppBar.module.scss'

const AppBar = (props) => {
  const { active, redirect, user } = props
  return (
    <nav className={styles.navContainer}>
      <div>
        <Logo className={styles.logo} />
        <ActivityIcon
          className={`${styles.navIcon} ${active === 'sim' && styles.active}`}
          onClick={() => redirect('/')}
        />
        <HelpIcon className={`${styles.navIcon} ${active === 'edu' && styles.active}`} />
        <MonitorIcon
          className={`${styles.navIcon} ${active === 'admin' && styles.active}`}
          onClick={() => redirect('/admin')}
        />
      </div>
      <div>
        <UserIcon className={`${styles.navIcon} ${active === 'user' && styles.active}`} />
        <LogOutIcon
          className={styles.navIcon}
          onClick={() => logout(redirect)}
        />
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
  user: state.persist.user,
})

export default connect(mapStateToProps, {})(AppBar)
