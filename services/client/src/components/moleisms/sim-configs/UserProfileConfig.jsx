import React from 'react'
import PropTypes from 'prop-types'
import TextField, { TextFieldExtra } from '../../elements/textfield'
import Checkbox from '../../elements/checkbox'

import styles from './UserProfileConfig.module.scss'

const UserProfileConfig = ({ values, onChange }) => (
  <React.Fragment>
    <Checkbox
      className={styles.checkbox}
      name="displayUserCurve"
      onChange={val => onChange('displayUserCurve', val)}
      isChecked={values.displayUserCurve}
      label="Show user profile"
    />
    <div className={`input-row ${styles.config}`}>
      <span>Start temperature</span>
      <TextFieldExtra
        type="text"
        name="start_temp"
        onChange={val => onChange('start_temp', val)}
        value={values.start_temp}
        length="short"
        suffix="°C"
      />
    </div>
    <div className={`input-row ${styles.config}`}>
      <span>Cooling rate -CCT</span>
      <TextFieldExtra
        type="text"
        name="cct_cooling_rate"
        onChange={val => onChange('cct_cooling_rate', val)}
        value={values.cct_cooling_rate}
        length="short"
        suffix="°C/sec"
        className={styles.textfield}
      />
    </div>
  </React.Fragment>
)

UserProfileConfig.propTypes = {
  values: PropTypes.shape({
    start_temp: PropTypes.number.isRequired,
    cct_cooling_rate: PropTypes.number.isRequired,
    displayUserCurve: PropTypes.bool.isRequired,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
}

export default UserProfileConfig
