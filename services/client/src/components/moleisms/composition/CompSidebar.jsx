/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Composition sidebar
 *
 * @version 1.2.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import CompForm from './CompForm'
import CompTable from './CompTable'
import Button from '../../elements/button'
import TimeTravelButtons from './TimeTravelButtons'
import { runSim } from '../../../state/ducks/sim/actions'

import styles from './CompSidebar.module.scss'

class CompSidebar extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showSettings: props.isAuthenticated,
    }
  }

  render() {
    const {
      runSimConnect,
      sessionIsInitialised,
      isAuthenticated,
      onSaveButtonClick,
      configError,
      parentError,
    } = this.props
    const { showSettings } = this.state

    return (
      <div className={styles.sidebar}>
        <header>
          <h4>Composition</h4>
          {/* <Button
            appearance="text"
            onClick={() => this.setState(prevState => ({
              showSettings: !prevState.showSettings,
            }))}
            IconComponent={(props) => {
              if (showSettings) return <ChevronUpIcon {...props} />
              return <ChevronDownIcon {...props} />
            }}
            isDisabled={!isAuthenticated}
          >
            {showSettings ? 'Collapse' : 'Expand'}
          </Button> */}
          <TimeTravelButtons />
        </header>
        <div style={{ display: showSettings ? 'block' : 'none' }}>
          <CompForm
            sessionIsInitialised={sessionIsInitialised}
            isAuthenticated={isAuthenticated}
            onSaveButtonClick={onSaveButtonClick}
          />
        </div>
        <div className={styles.table}>
          <CompTable />
        </div>
        <Button
          onClick={runSimConnect}
          length="long"
          className={styles.btn}
          isDisabled={
            !sessionIsInitialised
            || !isAuthenticated
            || Object.keys(configError).length !== 0
            || Object.keys(parentError).length !== 0
          }
        >
          RUN
        </Button>
      </div>
    )
  }
}

CompSidebar.propTypes = {
  onSaveButtonClick: PropTypes.func.isRequired,
  runSimConnect: PropTypes.func.isRequired,
  sessionIsInitialised: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  configError: PropTypes.shape({}).isRequired,
  parentError: PropTypes.shape({}).isRequired,
}

const mapStateToProps = state => ({
  configError: state.sim.configurations.error,
  parentError: state.sim.alloys.parentError,
})

const mapDispatchToProps = {
  runSimConnect: runSim,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompSidebar)
