import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { TextFieldExtra } from '../../elements/textfield'
import Checkbox from '../../elements/checkbox'
import { updateConfig, toggleDisplayUserCurve } from '../../../state/ducks/sim/actions'
import { validate } from '../../../utils/validator'
import { constraints } from './utils/constraints'

import styles from './UserProfileConfig.module.scss'

class UserProfileConfig extends Component {
  handleUpdateInput = (name, value) => {
    const { updateConfigConnect } = this.props
    let err
    if (name === 'start_temp') {
      err = validate(value, constraints.startTemp)
    } else err = validate(value, constraints.cctRate)

    if (err !== undefined) {
      updateConfigConnect(name, value, { [name]: err })
    } else updateConfigConnect(name, value, {})
  }

  render() {
    const {
      configurations,
      displayUserCurve,
      toggleDisplayUserCurveConnect,
      isAuthenticated,
    } = this.props
    return (
      <React.Fragment>
        <Checkbox
          className={styles.checkbox}
          name="displayUserCurve"
          onChange={val => toggleDisplayUserCurveConnect(val)}
          isChecked={displayUserCurve}
          label="Show user profile"
          isDisabled={!isAuthenticated}
        />
        <div className={`input-row ${styles.config}`}>
          <span>Start temperature</span>
          <TextFieldExtra
            type="text"
            name="start_temp"
            onChange={val => this.handleUpdateInput('start_temp', val)}
            value={configurations.start_temp}
            length="short"
            suffix="°C"
            isDisabled={!isAuthenticated}
            error={configurations.error.start_temp}
          />
        </div>
        <div className={`input-row ${styles.config}`}>
          <span>CCT cooling rate</span>
          <TextFieldExtra
            type="text"
            name="cct_cooling_rate"
            onChange={val => this.handleUpdateInput('cct_cooling_rate', val)}
            value={configurations.cct_cooling_rate}
            length="short"
            suffix="°C/sec"
            className={styles.textfield}
            isDisabled={!isAuthenticated}
            error={configurations.error.cct_cooling_rate}
          />
        </div>
      </React.Fragment>
    )
  }
}

UserProfileConfig.propTypes = {
  configurations: PropTypes.shape({
    start_temp: PropTypes.number.isRequired,
    cct_cooling_rate: PropTypes.number.isRequired,
  }).isRequired,
  displayUserCurve: PropTypes.bool.isRequired,
  updateConfigConnect: PropTypes.func.isRequired,
  toggleDisplayUserCurveConnect: PropTypes.func.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
}

const mapStateToProps = state => ({
  configurations: state.sim.configurations,
  displayUserCurve: state.sim.displayUserCurve,
})

const mapDispatchToProps = {
  updateConfigConnect: updateConfig,
  toggleDisplayUserCurveConnect: toggleDisplayUserCurve,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserProfileConfig)
