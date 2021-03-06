/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Checkbox component
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck } from '@fortawesome/pro-light-svg-icons/faCheck'
import CheckIcon from 'react-feather/dist/icons/check'

import styles from './Checkbox.module.scss'

// TODO: include validation
const Checkbox = (props) => {
  const {
    isDisabled = false,
    label = '',
    className = '',
    isChecked = false,
    name,
    onChange,
  } = props
  const classname = `${styles.checkbox} ${isDisabled && styles.disabled} ${className || ''}`

  return (
    <div className={classname}>
      <input
        type="checkbox"
        name={name}
        onChange={e => onChange(e.target.checked)}
        disabled={isDisabled}
        checked={isChecked}
      />
      <div className={styles.checkmark}>
        {/* <CheckIcon className={styles.icon} /> */}
        <FontAwesomeIcon icon={faCheck} className={styles.icon} size="2x" />
      </div>
      <span>{label}</span>
    </div>
  )
}

Checkbox.propTypes = {
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  isChecked: PropTypes.bool,
  label: PropTypes.string,
  isDisabled: PropTypes.bool,
  className: PropTypes.string,
}

Checkbox.defaultProps = {
  label: '',
  isDisabled: false,
  isChecked: false,
  className: '',
}

export default Checkbox
