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
import { loadPersistedSim, loadLastSim } from '../../../state/ducks/sim/actions'
import { getLastSim } from '../../../state/ducks/self/actions'
import { persistSim } from '../../../state/ducks/persist/actions'
import { logError } from '../../../api/LoggingHelper'

import styles from './EquiPage.module.scss'

class EquiPage extends React.Component {
  componentDidMount = () => {
    const {
      isInitialised,
      persistedSim,
      persistedSimTime,
      loadPersistedSimConnect,
      lastSim,
      getLastSimConnect,
      loadLastSimConnect,
    } = this.props

    // don't load anything if an alloy has already been chosen
    if (isInitialised) return

    const persistedTime = Date.parse(persistedSimTime)
    const now = new Date()
    const diff = now - persistedTime

    // if the last sim session is less than 1 hour ago, load it instead
    // otherwise, load the last sim saved in the account
    if (diff / 60000 < 60 && Object.keys(persistedSim).length !== 0) {
      loadPersistedSimConnect()
    } else if (lastSim === undefined || Object.keys(lastSim).length === 0) {
      getLastSimConnect()
        .then((res) => {
          if (res.status === 'success') {
            loadLastSimConnect()
          }
        })
        .catch((err) => logError(
          err.toString(), err.message, 'EquiPage.componentDidMount', err.stack_trace,
        ))
    }
  }

  render() {
    const {
      history,
      xfe,
      ceut,
      cf,
      isAdmin,
      isAuthenticated
    } = this.props
    return (
      <>
        <AppBar active="equilibrium" redirect={history.push} isAdmin={isAdmin} isAuthenticated={isAuthenticated} />
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
                <h6 className={styles.configLabel}>Ferrite phase fraction</h6>
                <span>{xfe}</span>
              </div>
              <div>
                <h6 className={styles.configLabel}>Eutectic Carbon content wt.</h6>
                <span>{ceut}</span>
              </div>
              <div>
                <h6 className={styles.configLabel}>Cf</h6>
                <span>{cf}</span>
              </div>
            </div>
          </section>
        </div>
      </>
    )
  }
}

EquiPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  // given by connect()
  xfe: PropTypes.number.isRequired,
  ceut: PropTypes.number.isRequired,
  cf: PropTypes.number.isRequired,
  isInitialised: PropTypes.bool.isRequired,
  loadPersistedSimConnect: PropTypes.func.isRequired,
  getLastSimConnect: PropTypes.func.isRequired,
  loadLastSimConnect: PropTypes.func.isRequired,
  persistedSim: PropTypes.shape({}).isRequired,
  persistedSimTime: PropTypes.string.isRequired,
  lastSim: PropTypes.shape({}).isRequired,
  isAdmin: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
}

const mapStateToProps = (state) => ({
  xfe: state.equi.xfe,
  ceut: state.equi.ceut,
  cf: state.equi.cf,
  isInitialised: state.sim.isInitialised,
  persistedSim: state.persist.lastSim,
  persistedSimTime: state.persist.lastSimTime,
  lastSim: state.self.lastSim,
})

const mapDispatchToProps = {
  persistSimConnect: persistSim,
  loadPersistedSimConnect: loadPersistedSim,
  getLastSimConnect: getLastSim,
  loadLastSimConnect: loadLastSim,
}

export default connect(mapStateToProps, mapDispatchToProps)(EquiPage)
