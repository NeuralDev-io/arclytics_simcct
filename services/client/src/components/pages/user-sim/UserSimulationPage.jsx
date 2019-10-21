/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User saved simulation page rendered by '/user/simulations'
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserSavedSimulations from '../../moleisms/user-sim'

import styles from './UserSimulationPage.module.scss'

const UserSimulationPage = ({ history, isAdmin }) => (
  <>
    <AppBar active="savedSimulations" redirect={history.push} isAdmin={isAdmin} isAuthenticated />
    <div className={styles.main}>
      <UserSavedSimulations redirect={history.push} />
    </div>
  </>
)

UserSimulationPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
}

export default UserSimulationPage
