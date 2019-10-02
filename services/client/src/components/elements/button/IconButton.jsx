import React from 'react'
import PropTypes from 'prop-types'
import Tooltip from '../tooltip'
import { buttonize } from '../../../utils/accessibility'

import styles from './IconButton.module.scss'

const IconButton = ({
  isDisabled = false,
  className = {
    button: '',
    icon: '',
  },
  tooltipPosition = 'right',
  tooltipText = 'Button',
  Icon,
  onClick,
}) => {
  const classname = `${styles.button} ${isDisabled && styles.disabled} ${className.button}`
  return (
    <Tooltip position={tooltipPosition}>
      <div
        className={classname}
        {...(() => {
          if (isDisabled) return {}
          return buttonize(onClick)
        })()}
      >
        <Icon className={`${styles.icon} ${className.icon}`} />
      </div>
      <span>{tooltipText}</span>
    </Tooltip>
  )
}

IconButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  Icon: PropTypes.oneOfType([
    PropTypes.element,
    PropTypes.elementType,
  ]).isRequired,
  isDisabled: PropTypes.bool,
  className: PropTypes.shape({
    button: PropTypes.string,
    icon: PropTypes.string,
  }),
  tooltipText: PropTypes.string.isRequired,
  tooltipPosition: PropTypes.string,
}

IconButton.defaultProps = {
  isDisabled: false,
  className: {
    button: '',
    icon: '',
  },
  tooltipPosition: 'right',
}

export default IconButton
