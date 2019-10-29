/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Configurations for user profile simulation. Input elements in this
 * form are disabled until users choose an alloy using the CompForm
 * component.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
/* eslint-disable react/prop-types */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { TextFieldExtra } from '../../elements/textfield'
import Checkbox from '../../elements/checkbox'
import { updateConfig, toggleDisplayUserCurve } from '../../../state/ducks/sim/actions'
import { validate } from '../../../utils/validator'
import { constraints } from './utils/constraints'
import { ReactComponent as BrainIcon } from '../../../assets/icons/brain.svg'
import Tooltip from '../../elements/tooltip'

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
      isInitialised,
    } = this.props
    return (
      <>
        <Checkbox
          className={styles.checkbox}
          name="displayUserCurve"
          onChange={val => toggleDisplayUserCurveConnect(val)}
          isChecked={displayUserCurve}
          label="Show user profile"
          isDisabled={!isAuthenticated || !isInitialised}
        />
        <div className={`input-row ${styles.config}`}>
          <div className={styles.titleContainer}>
            <span>Start temperature</span>
            <Tooltip className={{ container: styles.infoTipContainer }}>
              <BrainIcon className={styles.infoIcon} />
              <p>
                Test
              </p>
            </Tooltip>
          </div>
          <TextFieldExtra
            type="text"
            name="start_temp"
            onChange={val => this.handleUpdateInput('start_temp', val)}
            value={configurations.start_temp}
            length="short"
            suffix="°C"
            isDisabled={!isAuthenticated || !isInitialised}
            error={configurations.error.start_temp}
          />
        </div>
        <div className={`input-row ${styles.config}`}>
          <div className={styles.titleContainer}>
            <span>CCT cooling rate</span>
            <Tooltip className={{ container: styles.infoTipContainer }}>
              <BrainIcon className={styles.infoIcon} />
              <p>
                Test
              </p>
            </Tooltip>
          </div>
          <TextFieldExtra
            type="text"
            name="cct_cooling_rate"
            onChange={val => this.handleUpdateInput('cct_cooling_rate', val)}
            value={configurations.cct_cooling_rate}
            length="short"
            suffix="°C/sec"
            className={styles.textfield}
            isDisabled={!isAuthenticated || !isInitialised}
            error={configurations.error.cct_cooling_rate}
          />
        </div>
      </>
    )
  }
}

UserProfileConfig.propTypes = {
  isInitialised: PropTypes.bool.isRequired,
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
  isInitialised: state.sim.isInitialised,
})

const mapDispatchToProps = {
  updateConfigConnect: updateConfig,
  toggleDisplayUserCurveConnect: toggleDisplayUserCurve,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserProfileConfig)
