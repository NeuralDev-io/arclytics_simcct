/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Equilibrium chart rendered by '/equilibrium'
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import Equilibrium from '../../moleisms/charts/Equilibrium'

import styles from './EquiPage.module.scss'

const EquiPage = ({ history }) => (
  <React.Fragment>
    <AppBar active="equilibrium" redirect={history.push} isAdmin isAuthenticated />
    <div className={styles.main}>
      <h4>Ae3 equilibrium</h4>
      <div className={styles.chart}>
        <Equilibrium />
      </div>
    </div>
  </React.Fragment>
)

EquiPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

export default EquiPage
