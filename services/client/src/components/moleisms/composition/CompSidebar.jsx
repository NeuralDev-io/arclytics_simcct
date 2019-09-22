import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
// import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
// import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
import CompForm from './CompForm'
import CompTable from './CompTable'
import Button from '../../elements/button'
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
        </header>
        <div style={{ display: showSettings ? 'block' : 'none' }}>
          <CompForm isAuthenticated={isAuthenticated} />
        </div>
        <div className={styles.table}>
          <CompTable
            sessionIsInitialised={sessionIsInitialised}
            isAuthenticated={isAuthenticated}
            onSaveButtonClick={onSaveButtonClick}
          />
        </div>
        <Button
          onClick={runSimConnect}
          length="long"
          className={styles.btn}
          isDisabled={!sessionIsInitialised
            || !isAuthenticated
            || !(Object.keys(configError).length === 0 && configError.constructor === Object)
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
}

const mapStateToProps = state => ({
  configError: state.sim.configurations.error,
})

const mapDispatchToProps = {
  runSimConnect: runSim,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompSidebar)
