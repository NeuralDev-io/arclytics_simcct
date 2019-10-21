/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * File input component.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'

import styles from './FileInput.module.scss'

function FileInput({
  name,
  placeholder,
  Icon,
  onChange,
  className,
  filename,
  ...other
}) {
  return (
    <label htmlFor={name} className={styles.label}>
      <input
        type="file"
        name={name}
        id={name}
        placeholder={placeholder}
        className={styles.inputfile}
        onChange={onChange}
      />
      <div className={`${styles.labelText} ${className}`} {...other}>
        {Icon !== null && <Icon className={styles.icon} />}
        {filename !== '' ? filename : placeholder}
      </div>
    </label>
  )
}

FileInput.propTypes = {
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  Icon: PropTypes.elementType,
  onChange: PropTypes.string.isRequired,
  className: PropTypes.string,
  filename: PropTypes.string,
}

FileInput.defaultProps = {
  placeholder: 'Choose a file',
  Icon: null,
  className: '',
  filename: '',
}

export default FileInput
