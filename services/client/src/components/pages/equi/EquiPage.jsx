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
import { connect } from 'react-redux'
import AppBar from '../../moleisms/appbar'
import Equilibrium from '../../moleisms/charts/Equilibrium'

import styles from './EquiPage.module.scss'

const EquiPage = ({
  history,
  xfe,
  ceut,
  cf,
}) => (
  <React.Fragment>
    <AppBar active="equilibrium" redirect={history.push} isAdmin isAuthenticated />
    <div className={styles.main}>
      <section>
        <h4>Ae3 equilibrium</h4>
        <div className={styles.chart}>
          <Equilibrium />
        </div>
      </section>
      <section className={styles.configs}>
        <h4>Configurations</h4>
        <div className={styles.configs}>
          <div>
            <h6 className={styles.configLabel}>Xfe</h6>
            <span>{xfe}</span>
          </div>
          <div>
            <h6 className={styles.configLabel}>Ceut</h6>
            <span>{ceut}</span>
          </div>
          <div>
            <h6 className={styles.configLabel}>Cf</h6>
            <span>{cf}</span>
          </div>
        </div>
      </section>
    </div>
  </React.Fragment>
)

EquiPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  // given by connect()
  xfe: PropTypes.number.isRequired,
  ceut: PropTypes.number.isRequired,
  cf: PropTypes.number.isRequired,
}

const mapStateToProps = (state) => ({
  xfe: state.equi.xfe,
  ceut: state.equi.ceut,
  cf: state.equi.cf,
})

export default connect(mapStateToProps, {})(EquiPage)
