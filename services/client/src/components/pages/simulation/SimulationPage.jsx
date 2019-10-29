/* eslint-disable react/jsx-props-no-spreading */
/* eslint-disable camelcase */
/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Simulation page rendered by '/'
 *
 * @version 1.4.0
 * @author Dalton Le and Andrew Che
 */

import React, { Component } from 'react'
// noinspection ES6CheckImport
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronUp } from '@fortawesome/pro-light-svg-icons/faChevronUp'
import { faChevronDown } from '@fortawesome/pro-light-svg-icons/faChevronDown'
import Button from '../../elements/button'
import Modal from '../../elements/modal'
import AppBar from '../../moleisms/appbar'
import CompSidebar from '../../moleisms/composition'
import PhaseFractions from '../../moleisms/charts/PhaseFractions'
import { SaveAlloyModal } from '../../moleisms/user-alloys'
import { SignupModal } from '../../moleisms/demo'
import { ConfigForm, UserProfileConfig } from '../../moleisms/sim-configs'
import { SaveSimButton, ShareSimButton, LoadSimButton } from '../../moleisms/sim-actions'
import { TTT, CCT } from '../../moleisms/charts'
import { loadPersistedSim, loadLastSim } from '../../../state/ducks/sim/actions'
import { getLastSim } from '../../../state/ducks/self/actions'
import { persistSim } from '../../../state/ducks/persist/actions'
import { logError } from '../../../api/LoggingHelper'

import styles from './SimulationPage.module.scss'


class SimulationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      displayConfig: true,
      displayProfile: true,
      displaySaveModal: false,
    }
  }

  componentDidMount = () => {
    const {
      persistSimConnect,
      persistedSim,
      persistedSimTime,
      loadPersistedSimConnect,
      lastSim,
      getLastSimConnect,
      loadLastSimConnect,
      location,
    } = this.props
    window.addEventListener('beforeunload', persistSimConnect)

    // if sim already loaded from account, then don't load any cached sim
    if (location.state !== undefined && (
      location.state.loadFromAccount || location.state.loadFromShare
    )) return

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
          err.toString(), err.message, 'SimulationPage.componentDidMount', err.stack_trace,
        ))
    }
  }

  componentWillUnmount = () => {
    const { persistSimConnect } = this.props
    persistSimConnect()
    window.removeEventListener('beforeunload', persistSimConnect)
  }

  handleShowModal = () => this.setState({ displaySaveModal: true })

  handleCloseModal = () => this.setState({ displaySaveModal: false })

  render() {
    const {
      displayConfig,
      displayProfile,
      displaySaveModal,
    } = this.state
    const {
      history,
      isInitialised,
      isSimulated,
      isAdmin,
      isAuthenticated,
    } = this.props

    return (
      <>
        <AppBar active="sim" redirect={history.push} isAdmin={isAdmin} isAuthenticated={isAuthenticated} />
        <div className={styles.compSidebar}>
          <CompSidebar
            sessionIsInitialised={isInitialised}
            isAuthenticated={isAuthenticated}
            onSaveButtonClick={this.handleShowModal}
          />
        </div>
        <div className={styles.main}>
          <header>
            <div className={styles.config}>
              <h4>Configurations</h4>
              <Button
                appearance="text"
                onClick={() => this.setState(prevState => ({
                  displayConfig: !prevState.displayConfig,
                }))}
                IconComponent={(props) => {
                  if (displayConfig) return <FontAwesomeIcon icon={faChevronUp} {...props} />
                  return <FontAwesomeIcon icon={faChevronDown} {...props} />
                }}
              >
                {displayConfig ? 'Collapse' : 'Expand'}
              </Button>
            </div>
            <div className={styles.actions}>
              <ShareSimButton
                isSimulated={isSimulated}
                isAuthenticated={isAuthenticated}
              />
              <SaveSimButton
                isSimulated={isSimulated}
                isAuthenticated={isAuthenticated}
              />
              <LoadSimButton />
            </div>
          </header>
          <div className={styles.configForm} style={{ display: displayConfig ? 'block' : 'none' }}>
            <ConfigForm isAuthenticated={isAuthenticated} />
          </div>
          <div className={styles.results}>
            <h4>Results</h4>
            <div className={styles.charts}>
              {/* NOTE: TTT Child Component */}
              <div className={styles.line}>
                <h5>TTT</h5>
                <div id="ttt_chart">
                  <TTT />
                </div>
              </div>
              <div className={styles.line}>
                {/* NOTE: CCT Child Component */}
                <h5>CCT</h5>
                <div id="cct_chart">
                  <CCT />
                </div>
              </div>
            </div>
          </div>
          <div className={styles.custom}>
            <header>
              <h4>User cooling profile</h4>
              <Button
                appearance="text"
                onClick={() => this.setState(prevState => ({
                  displayProfile: !prevState.displayProfile,
                }))}
                IconComponent={props => (
                  displayProfile
                    ? <FontAwesomeIcon icon={faChevronUp} {...props} />
                    : <FontAwesomeIcon icon={faChevronDown} {...props} />
                )}
              >
                {displayProfile ? 'Collapse' : 'Expand'}
              </Button>
            </header>
            <div style={{ display: displayProfile ? 'flex' : 'none' }}>
              <div className={styles.userConfig}>
                <UserProfileConfig isAuthenticated={isAuthenticated} />
              </div>
              <PhaseFractions />
            </div>
          </div>
        </div>
        <Modal
          show={displaySaveModal}
          clicked={this.handleCloseModal}
          onClose={this.handleCloseModal}
        >
          <SaveAlloyModal handleClose={this.handleCloseModal} />
        </Modal>
        <SignupModal show={!isAuthenticated} redirect={history.push} />
      </>
    )
  }
}

SimulationPage.propTypes = {
  globalAlloys: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      symbol: PropTypes.string,
      weight: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    })),
  })).isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape({
      loadFromAccount: PropTypes.bool,
      loadFromShare: PropTypes.bool,
    }),
  }).isRequired,
  isInitialised: PropTypes.bool.isRequired,
  isSimulated: PropTypes.bool.isRequired,
  isAdmin: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  persistSimConnect: PropTypes.func.isRequired,
  loadPersistedSimConnect: PropTypes.func.isRequired,
  getLastSimConnect: PropTypes.func.isRequired,
  loadLastSimConnect: PropTypes.func.isRequired,
  persistedSim: PropTypes.shape({}).isRequired,
  persistedSimTime: PropTypes.string.isRequired,
  lastSim: PropTypes.shape({}).isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
  isInitialised: state.sim.isInitialised,
  isSimulated: state.sim.isSimulated,
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

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(SimulationPage))
