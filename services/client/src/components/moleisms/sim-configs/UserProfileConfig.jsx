import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { TextFieldExtra } from '../../elements/textfield'
import Checkbox from '../../elements/checkbox'
import { updateConfig, toggleDisplayUserCurve } from '../../../state/ducks/sim/actions'

import styles from './UserProfileConfig.module.scss'

const UserProfileConfig = ({
  configurations,
  displayUserCurve,
  updateConfigConnect,
  toggleDisplayUserCurveConnect,
  isAuthenticated,
}) => (
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
        onChange={val => updateConfigConnect('start_temp', val)}
        value={configurations.start_temp}
        length="short"
        suffix="°C"
        isDisabled={!isAuthenticated}
      />
    </div>
    <div className={`input-row ${styles.config}`}>
      <span>CCT cooling rate</span>
      <TextFieldExtra
        type="text"
        name="cct_cooling_rate"
        onChange={val => updateConfigConnect('cct_cooling_rate', val)}
        value={configurations.cct_cooling_rate}
        length="short"
        suffix="°C/sec"
        className={styles.textfield}
        isDisabled={!isAuthenticated}
      />
    </div>
  </React.Fragment>
)

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
