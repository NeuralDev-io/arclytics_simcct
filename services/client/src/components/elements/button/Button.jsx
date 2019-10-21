/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Button component.
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import PropTypes from 'prop-types'
import { InlineSpinner } from '../spinner'

import styles from './Button.module.scss'

const Button = (props) => {
  const {
    type = 'button',
    appearance = 'default',
    length = '',
    color = '',
    isDisabled = false,
    IconComponent = null,
    className,
    isLoading,
    onClick,
    children,
  } = props
  const classname = `${(appearance === 'default' || appearance === 'text' || appearance === 'outline') && styles[appearance]}
    ${(length === 'short' || length === 'long') && styles[length]}
    ${(color === 'dangerous' || color === 'warning') && styles[color]} ${isDisabled ? styles.disabled : ''} text--btn ${className || ''}`

  return (
    // eslint-disable-next-line react/button-has-type
    <button className={classname} onClick={onClick} type={type} disabled={isDisabled}>
      {(() => {
        if (isLoading) return <InlineSpinner />
        if (IconComponent !== null) {
          return (
            <>
              <IconComponent className={styles.icon} />
              {children}
            </>
          )
        }
        return children
      })()}
    </button>
  )
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.string,
  className: PropTypes.string,
  isLoading: PropTypes.bool,
  isDisabled: PropTypes.bool,
  /* appearance?: "default" | "outline" | "text" */
  appearance: PropTypes.string,
  /* color?: "dangerous" | "warning" */
  color: PropTypes.string,
  /* length?: "short" | "long" */
  length: PropTypes.string,
  onClick: PropTypes.func.isRequired,
  IconComponent: PropTypes.elementType,
}

Button.defaultProps = {
  type: 'button',
  className: '',
  isLoading: false,
  appearance: 'default',
  length: '',
  color: '',
  isDisabled: false,
  IconComponent: null,
}

export default Button
