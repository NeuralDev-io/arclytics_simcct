/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Self-controlled text field component
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import TextField from './TextField'

class SelfControlledTextField extends Component {
  constructor(props) {
    super(props)
    this.state = {
      value: props.defaultValue,
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
      defaultValue,
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

SelfControlledTextField.propTypes = {
  onChange: PropTypes.func,
  defaultValue: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
}

SelfControlledTextField.defaultProps = {
  onChange: () => {},
  defaultValue: '',
}

export default SelfControlledTextField
