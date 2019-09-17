import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserSavedSimulations from '../../moleisms/user-sim'

import styles from './UserSimulationPage.module.scss'

const UserSimulationPage = ({ history, isAdmin }) => (
  <React.Fragment>
    <AppBar active="savedSimulations" redirect={history.push} isAdmin={isAdmin} isAuthenticated />
    <div className={styles.main}>
      <UserSavedSimulations redirect={history.push} />
    </div>
  </React.Fragment>
)

UserSimulationPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
}

export default UserSimulationPage
