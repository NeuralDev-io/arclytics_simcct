import React from 'react'
import PropTypes from 'prop-types'
import { buttonize } from '../../../utils/accessibility'

import styles from './IconButton.module.scss'

const IconButton = ({
  isDisabled = false,
  className = '',
  Icon,
  onClick,
}) => {
  const classname = `${styles.button} ${isDisabled && styles.disabled} ${className}`
  return (
    <div className={classname} {...buttonize(onClick)}>
      <Icon className={styles.icon} />
    </div>
  )
}

IconButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  Icon: PropTypes.oneOfType([
    PropTypes.element,
    PropTypes.elementType,
  ]).isRequired,
  isDisabled: PropTypes.bool,
  className: PropTypes.string,
}

IconButton.defaultProps = {
  isDisabled: false,
  className: '',
}

export default IconButton
