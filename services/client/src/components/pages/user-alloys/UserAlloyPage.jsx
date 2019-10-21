/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User alloy page rendered by '/user/alloys'
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserAlloys from '../../moleisms/user-alloys'

import styles from './UserAlloyPage.module.scss'

const UserAlloyPage = ({ history, isAdmin }) => (
  <>
    <AppBar active="userAlloys" redirect={history.push} isAdmin={isAdmin} isAuthenticated />
    <div className={styles.main}>
      <UserAlloys history={history} />
    </div>
  </>
)

UserAlloyPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
}

export default UserAlloyPage
