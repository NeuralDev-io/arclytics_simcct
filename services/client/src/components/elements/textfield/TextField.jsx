/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Text field component
 *
 * @version 0.0.0
 * @author Dalton Le
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './TextField.module.scss'

// TODO: include validation
class TextField extends Component {
  validate = () => {
    const { validation, name } = this.props
    console.log(name, ' : ', validation)
    // do stuff
  }

  handleChange = (e) => {
    const { onChange } = this.props
    onChange(e.target.value)
  }

  render() {
    const {
      placeholder = 'Input',
      isDisabled = false,
      type = 'text',
      className = '',
      value = '',
      length = 'default',
      name,
      ...other
    } = this.props
    const classname = `${styles.input} ${length === 'default' ? '' : styles[length]} ${className || ''}`

    return (
      <div>
        <input
          {...other}
          type={type}
          className={classname}
          placeholder={placeholder}
          name={name}
          value={value}
          onChange={e => this.handleChange(e)}
          disabled={isDisabled}
          validation={this.validate()}
        />
      </div>
    )
  }
}

TextField.propTypes = {
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  length: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  type: PropTypes.string,
  placeholder: PropTypes.string,
  isDisabled: PropTypes.bool,
  className: PropTypes.string,
  validation: PropTypes.string,

}

TextField.defaultProps = {
  type: 'text',
  length: 'default',
  placeholder: 'Input',
  isDisabled: false,
  className: '',
  value: '',
  validation: '',
}

export default TextField
