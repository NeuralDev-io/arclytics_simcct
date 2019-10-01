import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import UndoIcon from 'react-feather/dist/icons/rotate-ccw'
import RedoIcon from 'react-feather/dist/icons/rotate-cw'
import CompForm from './CompForm'
import CompTable from './CompTable'
import Button, { IconButton } from '../../elements/button'
import { runSim } from '../../../state/ducks/sim/actions'
import { timeTravelBack, timeTravelNext } from '../../../state/ducks/timeMachine/actions'

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
      timeTravelBackConnect,
      timeTravelNextConnect,
      sessionIsInitialised,
      isAuthenticated,
      onSaveButtonClick,
      configError,
      parentError,
      timeMachine,
    } = this.props
    const { showSettings } = this.state

    console.log(timeMachine.data.length)
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
          <IconButton
            onClick={timeTravelBackConnect}
            Icon={props => <UndoIcon {...props} />}
            isDisabled={
              timeMachine.data.length === 0
              || timeMachine.current === 0
            }
          />
          <IconButton
            onClick={timeTravelNextConnect}
            Icon={props => <RedoIcon {...props} />}
            isDisabled={
              timeMachine.data.length === 0
              || timeMachine.current === timeMachine.data.length - 1
            }
          />
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
          isDisabled={!sessionIsInitialised
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
  timeTravelBackConnect: PropTypes.func.isRequired,
  timeTravelNextConnect: PropTypes.func.isRequired,
  sessionIsInitialised: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  configError: PropTypes.shape({}).isRequired,
  parentError: PropTypes.shape({}).isRequired,
  timeMachine: PropTypes.shape({
    data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
    current: PropTypes.number,
  }).isRequired,
}

const mapStateToProps = state => ({
  configError: state.sim.configurations.error,
  parentError: state.sim.alloys.parentError,
  timeMachine: state.timeMachine,
})

const mapDispatchToProps = {
  runSimConnect: runSim,
  timeTravelBackConnect: timeTravelBack,
  timeTravelNextConnect: timeTravelNext,
}

export default connect(mapStateToProps, mapDispatchToProps)(CompSidebar)
