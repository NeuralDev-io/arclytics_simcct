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

import styles from './styles.module.scss'

// TODO: Add styling support for buttons with icons
const Button = (props) => {
  const {
    type = 'button',
    appearance = 'default',
    length = 'default',
    isDisabled = false,
    className,
    isLoading,
    onClick,
    children,
  } = props
  const classname = `${styles[appearance]} ${styles[length]} ${isDisabled ? styles.disabled : ''} text--btn ${className || ''}`

  return (
    // eslint-disable-next-line react/button-has-type
    <button className={classname} onClick={onClick} type={type} disabled={isDisabled}>
      {
        isLoading
          ? <InlineSpinner />
          : children
      }
    </button>
  )
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.string,
  className: PropTypes.string,
  isLoading: PropTypes.bool,
  isDisabled: PropTypes.bool,
  /* appearance?: "default" | "outline" | "text" | "dangerous" | "warning"  */
  appearance: PropTypes.string,
  /* length?: "default" | "short" | "long" */
  length: PropTypes.string,
  onClick: PropTypes.func.isRequired,
}

Button.defaultProps = {
  type: 'button',
  className: '',
  isLoading: false,
  appearance: 'default',
  length: 'default',
  isDisabled: false,
}

export default Button
