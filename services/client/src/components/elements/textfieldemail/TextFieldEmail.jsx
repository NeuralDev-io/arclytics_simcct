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
        // sets error to null so that after error when a user starts to type, the error disappears
        error: null,
      })
  }

  // triggered when one of the following keys is pressed: ('Enter', 'Tab', 'Space', 'Comma')
  handleKeyDown = (e) => {
    if (['Enter', 'Tab', 'Space', ','].includes(e.key)) {
      /**
       * The preventDefault() method cancels the event if it is cancellable.
       * This essentially stops the keys from doing their original function
       * e.g. stops tab from going to next input, stops enter from submitting
       * the form, etc.
       **/
      e.preventDefault()
      const email = this.state.value.trim()

      // the following validates the email and check that input is not empty
      if (email && this.isValid(email)) {
        this.setState({
          emails: [...this.state.emails, email],
          value: '',
        })
      }
    }
  }

  // Triggered when the delete button next to an email is pressed
  handleDelete = (toBeRemoved) => {
    this.setState({
      //delete emails equal to the toBeRemoved argument
      emails: this.state.emails.filter(email => email !== toBeRemoved)
    })
  }

  // Triggered when called in the 'handleKeyDown' function
  isValid(email){
    let error = null

    // calls isEmail function to check if what user wrote is an email
    if (!this.isEmail(email)) {
      error = '"' + email + '" is not a valid email address.'
    }

    // calls isInList function to check if what user wrote already exists in emails[] array
    if (this.isInList(email)) {
      error = '"' + email + '" has already been added.'
    }

    // checks if an error exists in any of the above validations
    if (error) {
      this.setState({
        error
      })
      return false
    }

    return true
  }

  // checks if the email contains an @ symbol and at least one period
  isEmail(email){
    return /[\w\d\.-]+@[\w\d\.-]+\.[\w\d\.-]+/.test(email)
  }

  // checks if email already exists in the emails[] array
  isInList(email){
    return this.state.emails.includes(email)
  }

  /**
   * Triggered when user uses 'CTRL+V' or selects paste from right-click dialogue
   *
   * validation is also done here and not above because if the email is incorrect
   * on paste, funky things will happen.
   **/
  handlePaste = (e) => {
    // prevent default to stop email from being pasted as validation needs to be done before this.
    e.preventDefault()

    let paste = e.clipboardData.getData('text') // get the clipboard data
    let emails = paste.match(/[\w\d\.-]+@[\w\d\.-]+\.[\w\d\.-]+/g) // validate email format

    // check paste is not empty and add it to array
    if (emails) {
      let toBeAdded = emails.filter(email => !this.isInList(email))

      this.setState({
        emails: [...this.state.emails, ...toBeAdded]
      })
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
        <!--Email Chips-->
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
        <!--Input Field-->
        <input
          {...other}
          type={type}
          className={classname}
          placeholder={placeholder}
          name={name}
          value={this.state.value}
          onChange={e => this.handleChange(e)}
          onKeyDown={e => this.handleKeyDown(e)}
          onPaste={e => this.handlePaste(e)}
          disabled={isDisabled}
        />
        <!--Error message-->
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
