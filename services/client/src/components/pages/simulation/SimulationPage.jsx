/* eslint-disable camelcase */
/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Composition sidebar
 *
 * @version 0.8.0
 * @author Dalton Le and Andrew Che
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
import Button from '../../elements/button'
import AppBar from '../../moleisms/appbar'
import CompSidebar from '../../moleisms/composition'
import PhaseFractions from '../../moleisms/charts/PhaseFractions'
import { ConfigForm, UserProfileConfig } from '../../moleisms/sim-configs'
import { SaveSimButton, ShareSimButton, LoadSimButton } from '../../moleisms/sim-actions'
import { TTT, CCT } from '../../moleisms/charts'
import { postSaveSimulation } from '../../../api/sim/SessionSaveSim'

import styles from './SimulationPage.module.scss'

class SimulationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      displayConfig: true,
      displayProfile: true,
    }
  }

  componentDidMount = () => {
    // if (!localStorage.getItem('token')) {
    //   this.props.history.push('/signin') // eslint-disable-line
    // }
  }

  // handleShowModal = type => this.setState({ [`${type}Modal`]: true })

  // handleCloseModal = type => this.setState({ [`${type}Modal`]: false })

  saveCurrentSimulation = () => {
    const { configurations, alloys } = this.state
    console.log(configurations)
    const alloyStore = {
      alloy_option: alloys.alloyOption,
      alloys: {
        parent: alloys.parent,
        weld: alloys.weld,
        mix: alloys.mix,
      },
    }
    const { grain_size_ASTM, grain_size_diameter, ...others } = configurations
    const validConfigs = {
      ...others,
      grain_size: grain_size_ASTM,
    }
    console.log(alloyStore)
    postSaveSimulation(validConfigs, alloyStore)
  }

  render() {
    const {
      displayConfig,
      displayProfile,
      runSimConnect,
    } = this.state
    const { history, isInitialised } = this.props

    return (
      <React.Fragment>
        <AppBar active="sim" redirect={history.push} />
        <div className={styles.compSidebar}>
          <CompSidebar
            sessionIsInitialised={isInitialised}
            onSimulate={runSimConnect}
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
                  if (displayConfig) return <ChevronUpIcon {...props} />
                  return <ChevronDownIcon {...props} />
                }}
              >
                {displayConfig ? 'Collapse' : 'Expand'}
              </Button>
            </div>
            <div className={styles.actions}>
              <ShareSimButton isSessionInitialised={isInitialised} />
              <SaveSimButton isSessionInitialised={isInitialised} />
              <LoadSimButton />
            </div>
          </header>
          <div className={styles.configForm} style={{ display: displayConfig ? 'block' : 'none' }}>
            <ConfigForm />
          </div>
          <div className={styles.results}>
            <h4>Results</h4>
            <div className={styles.charts}>
              {/* NOTE: TTT Child Component */}
              <div className={styles.line}>
                <h5>TTT</h5>
                <div>
                  <TTT />
                </div>
              </div>
              <div className={styles.line}>
                {/* NOTE: CCT Child Component */}
                <h5>CCT</h5>
                <div>
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
                    ? <ChevronUpIcon {...props} />
                    : <ChevronDownIcon {...props} />
                )}
              >
                {displayProfile ? 'Collapse' : 'Expand'}
              </Button>
            </header>
            <div style={{ display: displayProfile ? 'flex' : 'none' }}>
              <div className={styles.userConfig}>
                <UserProfileConfig />
              </div>
              <PhaseFractions />
            </div>
          </div>
        </div>
      </React.Fragment>
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
  isInitialised: PropTypes.bool.isRequired,
}

const mapStateToProps = state => ({
  globalAlloys: state.alloys.global,
  isInitialised: state.sim.isInitialised,
})

const mapDispatchToProps = {}

export default connect(mapStateToProps, mapDispatchToProps)(SimulationPage)
