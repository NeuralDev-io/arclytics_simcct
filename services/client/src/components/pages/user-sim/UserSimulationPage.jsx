import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserSavedSimulations from '../../moleisms/user-sim'

import styles from './UserSimulationPage.module.scss'

const UserSimulationPage = ({ history }) => (
  <React.Fragment>
    <AppBar active="savedSimulations" redirect={history.push} />
    <div className={styles.main}>
      <UserSavedSimulations />
    </div>
  </React.Fragment>
)

UserSimulationPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
}

export default UserSimulationPage