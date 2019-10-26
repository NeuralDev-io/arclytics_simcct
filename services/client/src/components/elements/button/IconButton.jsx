/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Icon button component. A round button with only an icon and no name.
 *
 * @version 1.1.0
 * @author Dalton Le
 */
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
  withTooltip = false,
  tooltipPosition = 'right',
  tooltipText = 'Button',
  Icon,
  onClick,
}) => {
  const classname = `${styles.button} ${isDisabled && styles.disabled} ${className.button}`
  if (withTooltip) {
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
  return (
    <div
      className={classname}
      {...(() => {
        if (isDisabled) return {}
        return buttonize(onClick)
      })()}
    >
      <Icon className={`${styles.icon} ${className.icon}`} />
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
  className: PropTypes.shape({
    button: PropTypes.string,
    icon: PropTypes.string,
  }),
  withTooltip: PropTypes.bool,
  tooltipText: PropTypes.string,
  tooltipPosition: PropTypes.string,
}

IconButton.defaultProps = {
  isDisabled: false,
  className: {
    button: '',
    icon: '',
  },
  withTooltip: false,
  tooltipText: 'Click me',
  tooltipPosition: 'right',
}

export default IconButton
