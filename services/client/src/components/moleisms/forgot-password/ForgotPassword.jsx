import React, { Component } from 'react'
import PropTypes from 'prop-types'
import styles from '../../pages/login/LoginPage.module.scss'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import { forgotPasswordEmail } from '../../../utils/ValidationHelper'
import { forgotPassword } from '../../../api/AuthenticationHelper'
import { buttonize } from '../../../utils/accessibility'

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
          console.log(err)
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
      <React.Fragment>
        <h3 className={styles.header}> Password Reset </h3>
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
          <h6 className={emailSent ? styles.confirmation : styles.errors}>
            {emailSent ? ('Email has been sent.') : forgotPwdErr}
            &nbsp;
          </h6>
          <Button
            className={styles.forgotSubmit}
            type="submit"
            length="long"
            isDisabled={emailSent}
            onClick={this.handleForgotPasswordEmail}
          >
            Send Email
          </Button>
          <h6
            className={styles.help}
            {...buttonize(forgotPwdHandler)}
          >
            Go back to login
          </h6>
        </div>
      </React.Fragment>
    )
  }
}

ForgotPassword.propTypes = {
  forgotPwdHandler: PropTypes.func.isRequired,
}

export default ForgotPassword
