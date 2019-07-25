/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Uncontrolled text field component
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import TextField from './TextField'

// TODO: include validation
class UncontrolledTextField extends Component {
  constructor(props) {
    super(props)
    this.state = {
      value: props.value,
    }
  }

  handleChange = (val) => {
    const { onChange } = this.props
    this.setState({ value: val })
    onChange(val)
  }

  render() {
    const {
      onChange,
      ...other
    } = this.props
    const { value } = this.state

    return (
      <TextField
        {...other}
        onChange={val => this.handleChange(val)}
        value={value}
      />
    )
  }
}

UncontrolledTextField.propTypes = {
  onChange: PropTypes.func,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
}

UncontrolledTextField.defaultProps = {
  onChange: () => {},
  value: '',
}

export default UncontrolledTextField
