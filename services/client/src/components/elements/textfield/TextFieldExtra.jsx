import React from 'react'
import PropTypes from 'prop-types'
import TextField from './TextField'

import styles from './TextFieldExtra.module.scss'

const TextFieldExtra = (props) => {
  const {
    prefix,
    suffix,
    className,
    ...other
  } = props
  const classname = `${prefix !== '' && styles.withPrefix} ${suffix !== '' && styles.withSuffix}`

  return (
    <div className={styles.inputContainer}>
      {prefix !== '' && <span className={styles.prefix}>{prefix}</span>}
      <TextField
        {...other}
        className={classname}
      />
      {suffix !== '' && <span className={styles.suffix}>{suffix}</span>}
    </div>
  )
}

TextFieldExtra.propTypes = {
  prefix: PropTypes.string,
  suffix: PropTypes.string,
  className: PropTypes.string,
}

TextFieldExtra.defaultProps = {
  prefix: '',
  suffix: '',
  className: '',
}

export default TextFieldExtra
