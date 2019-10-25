/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * ForgotPassword: form to be displayed to help user recover
 * their password.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import { forgotPasswordEmail } from '../../../utils/ValidationHelper'
import { forgotPassword } from '../../../api/AuthenticationHelper'
import { buttonize } from '../../../utils/accessibility'
import { logError } from '../../../api/LoggingHelper'

import styles from '../../pages/login/LoginPage.module.scss'

class ForgotPassword extends Component {
  constructor(props) {
    super(props)
    this.state = {
      forgotPwdErr: '',
      emailSent: false,
      forgotEmail: '',
    }
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  handleForgotPasswordEmail = () => {
    const { forgotEmail } = this.state
    const validError = forgotPasswordEmail(forgotEmail)
    if (validError === '') {
      const promise = new Promise((resolve, reject) => {
        forgotPassword(resolve, reject, forgotEmail)
      })
      promise.then(() => {
        // If response is successful
        this.setState({
          forgotPwdErr: '',
          emailSent: true,
        })
      })
        .catch((err) => {
          // If response is unsuccessful
          logError(err.toString(), err.message, 'ForgotPassword.handleForgotPasswordEmail', err.stack)
          this.setState({
            forgotPwdErr: err,
          })
        })
    } else {
      this.setState({
        forgotPwdErr: validError,
      })
    }
  }

  render() {
    const { forgotEmail, forgotPwdErr, emailSent } = this.state
    const { forgotPwdHandler } = this.props
    return (
      <>
        <h3 className={styles.header}>Reset your password </h3>
        <span> Enter your email to send a password reset email.</span>
        <TextField
          name="forgotEmail"
          type="email"
          value={forgotEmail}
          onChange={value => this.handleChange('forgotEmail', value)}
          placeholder="Email"
          error={forgotPwdErr}
          length="stretch"
        />
        <div>
          <h6 className={styles.confirmation}>
            {emailSent ? ('Email has been sent.') : ('')}
            &nbsp;
          </h6>
          <div className={styles.buttonGroup}>
            <Button
              className={styles.forgotSubmit}
              type="submit"
              length="long"
              isDisabled={emailSent}
              onClick={this.handleForgotPasswordEmail}
            >
              Send Email
            </Button>
            <h6{...buttonize(forgotPwdHandler)}>
              Go back to login
            </h6>
          </div>
        </div>
      </>
    )
  }
}

ForgotPassword.propTypes = {
  forgotPwdHandler: PropTypes.func.isRequired,
}

export default ForgotPassword
