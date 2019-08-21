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
 * @author Dalton Le, Matthew Greentree
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import TextField from './TextField'

import styles from './TextFieldEmail.module.scss'

// TODO: include validation
class TextFieldEmail extends Component {
  constructor(props) {
    super(props)
    this.state = {
      value: this.props.value,
      emails: [],
    }
  }

  handleChange = (e) => {
    console.log("test")
    const { onChange } = this.props
    onChange(e.target.value)
    // Check if the event includes one of these keys (',', 'Tab')
    if (['Enter', 'Tab', 'Space', ','].includes(e.key)) {
      console.log("it worked")
      this.handleKeyDown(e)
    }
  }

  handleKeyDown = (e) => {
    /**
     * The preventDefault() method cancels the event if it is cancellable.
     * This essentially stops the keys from doing their original function
     * e.g. stops tab from going to next input, stops enter from submitting
     * the form, etc.
     **/
    e.preventDefault()
    console.log(this.state.emailValue)
    const email = this.state.emailValue.trim()

    if (email) {
      this.setState({
        emails: [...this.state.emails, email],
        value: '',
      })


    console.log(this.state.emails)
    }
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
          onKeyDown={e => this.handleKeyDown(e)}
          disabled={isDisabled}
        />
      </div>
    )
  }
}

TextFieldEmail.propTypes = {
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

}

TextFieldEmail.defaultProps = {
  type: 'text',
  length: 'default',
  placeholder: 'Input',
  isDisabled: false,
  className: '',
  value: '',
}

export default TextFieldEmail
