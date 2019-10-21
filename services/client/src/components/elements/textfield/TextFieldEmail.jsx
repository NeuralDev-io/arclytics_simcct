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
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {faTimes } from '@fortawesome/pro-light-svg-icons/faTimes'
import { buttonize } from '../../../utils/accessibility'

import styles from './TextFieldEmail.module.scss'


// TODO: include validation
class TextFieldEmail extends Component {
  // Triggered when called in the 'handleKeyDown' function
  isValid = (email) => {
    let error = null

    // calls isEmail function to check if what user wrote is an email
    if (!this.isEmail(email)) {
      error = `"${email}" is not a valid email address`
    }

    // calls isInList function to check if what user wrote already exists in emails[] array
    if (this.isInList(email)) {
      error = `"${email}" has already been added`
    }

    // checks if an error exists in any of the above validations
    if (error) {
      const { onChange } = this.props
      onChange('', error)
      return false
    }
    return true
  }

  // checks if the email contains an @ symbol and at least one period
  isEmail = email => /[\w\d.-]+@[\w\d.-]+\.[\w\d.-]+/.test(email)

  // checks if email already exists in the emails[] array
  isInList = (email) => {
    const { emails } = this.props
    return emails.includes(email)
  }

  handleChange = (e) => {
    const { onChange } = this.props
    onChange(e.target.value)
  }

  // triggered when one of the following keys is pressed: ('Enter', 'Tab', 'Space', 'Comma')
  handleKeyDown = (e) => {
    const { current, onAdd } = this.props
    if (['Enter', 'Tab', 'Space', ','].includes(e.key)) {
      /**
       * The preventDefault() method cancels the event if it is cancellable.
       * This essentially stops the keys from doing their original function
       * e.g. stops tab from going to next input, stops enter from submitting
       * the form, etc.
       */
      e.preventDefault()
      const email = current.trim()

      // the following validates the email and check that input is not empty
      if (email && this.isValid(email)) {
        onAdd([email])
      }
    }
  }

  // Triggered when the delete button next to an email is pressed
  handleDelete = (toBeRemoved) => {
    const { onRemove } = this.props
    // TODO: Add animation for removing an email
    setTimeout(() => {
      onRemove(toBeRemoved)
    }, 100)
    // onRemove(toBeRemoved)
  }

  /**
   * Triggered when user uses 'CTRL+V' or selects paste from right-click dialogue
   *
   * validation is also done here and not above because if the email is incorrect
   * on paste, funky things will happen.
   */
  handlePaste = (e) => {
    // prevent default to stop email from being pasted as validation needs to be done before this.
    e.preventDefault()

    const paste = e.clipboardData.getData('text') // get the clipboard data
    const emails = paste.match(/[\w\d.-]+@[\w\d.-]+\.[\w\d.-]+/g) // validate email format

    // check paste is not empty and add it to array
    if (emails) {
      const toBeAdded = emails.filter(email => !this.isInList(email))
      const { onAdd } = this.props
      onAdd(toBeAdded)
    }
  }

  render() {
    const {
      placeholder = 'Input',
      isDisabled = false,
      type = 'text',
      className = '',
      length = 'default',
      name,
      emails,
      current,
      error,
      ...other
    } = this.props
    const classname = `${styles.input} ${length === 'default' ? '' : styles[length]} ${className || ''}`

    // TODO: ADD STYLING
    return (
      <div>
        <div className={styles.emails}>
          {emails.map(email => (
            <div
              className={styles.emailItem}
              key={email}
              {...buttonize(() => this.handleDelete(email))}
            >
              <span>{email}</span>
              <FontAwesomeIcon icon={faTimes} className={styles.icon} size="sm" />
            </div>
          ))}
        </div>
        <input
          {...other}
          type={type}
          className={classname}
          placeholder={placeholder}
          name={name}
          value={current}
          onChange={e => this.handleChange(e)}
          onKeyDown={e => this.handleKeyDown(e)}
          onPaste={e => this.handlePaste(e)}
          disabled={isDisabled}
        />
        <span className={styles.emailError}>{error}</span>
      </div>
    )
  }
}

TextFieldEmail.propTypes = {
  name: PropTypes.string.isRequired,
  length: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  type: PropTypes.string,
  placeholder: PropTypes.string,
  isDisabled: PropTypes.bool,
  className: PropTypes.string,

  emails: PropTypes.arrayOf(PropTypes.string).isRequired,
  current: PropTypes.string.isRequired,
  error: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onRemove: PropTypes.func.isRequired,
  onAdd: PropTypes.func.isRequired,
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
