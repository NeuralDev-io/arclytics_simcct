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

import styles from './TextFieldEmail.module.scss'

// TODO: include validation
class TextFieldEmail extends Component {
  constructor(props) {
    super(props)
    this.state = {
      value: '',
      emails: [],
      error: null,
    }
  }

  handleChange = (e) => {
      this.setState({
        value: e.target.value,
        error: null,
      })
  }

  handleKeyDown = (e) => {
    // Check if the event includes one of these keys (',', 'Tab')
    if (['Enter', 'Tab', 'Space', ','].includes(e.key)) {
      /**
       * The preventDefault() method cancels the event if it is cancellable.
       * This essentially stops the keys from doing their original function
       * e.g. stops tab from going to next input, stops enter from submitting
       * the form, etc.
       **/
      e.preventDefault()
      const email = this.state.value.trim()

      if (email && this.isValid(email)) {
        this.setState({
          emails: [...this.state.emails, email],
          value: '',
        })
      }
    }
  }

  handleDelete = (toBeRemoved) => {
    this.setState({
      //delete emails equal to the toBeRemoved argument
      emails: this.state.emails.filter(email => email !== toBeRemoved)
    })
  }

  isValid(email){
    let error = null

    if (!this.isEmail(email)) {
      error = '"' + email + '" is not a valid email address.'
    }

    if (this.isInList(email)) {
      error = '"' + email + '" has already been added.'
    }

    if (error) {
      this.setState({
        error
      })
      return false
    }

    return true
  }

  //
  isEmail(email){
    return /[\w\d\.-]+@[\w\d\.-]+\.[\w\d\.-]+/.test(email)
  }

  isInList(email){
    return this.state.emails.includes(email)
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
        {this.state.emails.map(email => (
          <div className="emailItem" key={email}>
            {email}&nbsp;
            <button
              type="button"
              onClick={() => this.handleDelete(email)}
            >
              &times;
            </button>
          </div>
        ))}
        <input
          {...other}
          type={type}
          className={classname}
          placeholder={placeholder}
          name={name}
          value={this.state.value}
          onChange={e => this.handleChange(e)}
          onKeyDown={e => this.handleKeyDown(e)}
          disabled={isDisabled}
        />
        <span className="emailError">{this.state.error}</span>
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
