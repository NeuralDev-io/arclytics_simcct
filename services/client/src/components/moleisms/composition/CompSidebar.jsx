import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
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
    const { runSimConnect, sessionIsInitialised, isAuthenticated } = this.props
    const { showSettings } = this.state

    return (
      <div className={styles.sidebar}>
        <header>
          <h4>Composition</h4>
          <Button
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
          </Button>
        </header>
        <div style={{ display: showSettings ? 'block' : 'none' }}>
          <CompForm />
        </div>
        <div className={styles.table}>
          <CompTable />
        </div>
        <Button
          onClick={runSimConnect}
          length="long"
          className={styles.btn}
          isDisabled={!sessionIsInitialised || !isAuthenticated}
        >
          RUN
        </Button>
      </div>
    )
  }
}

CompSidebar.propTypes = {
  runSimConnect: PropTypes.func.isRequired,
  sessionIsInitialised: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
}

const mapDispatchToProps = {
  runSimConnect: runSim,
}

export default connect(null, mapDispatchToProps)(CompSidebar)
