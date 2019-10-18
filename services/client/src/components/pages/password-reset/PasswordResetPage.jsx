/**
 * Password Reset Page
 *
 * @version 1.0.0
 * @author Arvy Salazar
 *
 * Provides the password reset page and the controller logic to accomplish a password
 * reset for the user after it has been successfully authenticated by the backend.
 *
 */

import React, { Component } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheckCircle } from '@fortawesome/pro-light-svg-icons/faCheckCircle'
import PropTypes from 'prop-types'
import { resetPassword, checkAuthStatus } from '../../../api/AuthenticationHelper'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { passwordResetValidation } from '../../../utils/ValidationHelper'

import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'

import styles from './PasswordResetPage.module.scss'
import { logError } from '../../../api/LoggingHelper'


class PasswordResetPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      newPwd: '',
      newPwdErr: '',
      cnfrmPwd: '',
      cnfrmPwdErr: '',
      status: '',
    }
    this.handleStatus = this.handleStatus.bind(this)
  }

  componentDidMount = () => {
    const { history } = this.props
    checkAuthStatus().then((res) => {
      if (res.status === 'success') {
        history.push('/')
      }
    })
  }

  handleStatus = () => {
    const { status } = this.state
    const { history } = this.props
    if (status === '') {
      return ('')
    }
    if (status === 'success') {
      return (
        <Modal className={styles.cnfrmModal} show="true">
          <FontAwesomeIcon icon={faCheckCircle} className={styles.checkCircleIcon} />
          <h5>
            Your account password has been successfully changed.
          </h5>
          <span>
            Click the button below to go back to the login page.
          </span>
          <Button length="long" onClick={() => { history.push('/signin') }}> Go to log in </Button>
        </Modal>
      )
    }
    return (<span className={styles.error}>{status}</span>)
  }

  handleSubmit = () => {
    const { match } = this.props
    const { newPwd, cnfrmPwd } = this.state
    const err = passwordResetValidation({ newPwd, cnfrmPwd })
    if (!(
      Object.prototype.hasOwnProperty.call(err, 'newPwdErr')
      || Object.prototype.hasOwnProperty.call(err, 'cnfrmPwdErr'))) {
      const promise = new Promise((resolve, reject) => {
        resetPassword(
          resolve,
          reject,
          {
            password: newPwd,
            confirm_password: cnfrmPwd,
          },
          match.params.token,
        )
      })
      promise.then(() => {
        // success
        this.setState({
          status: 'success',
        })
      })
        .catch((error) => {
          this.setState({
            status: err,
          })
          logError(error.toString(), error.message, 'PasswordResetPage.handleSubmit', error.stack)
        })
    } else {
      this.setState({
        newPwdErr: Object.prototype.hasOwnProperty.call(err, 'newPwdErr') ? err.newPwdErr : (''),
        cnfrmPwdErr: Object.prototype.hasOwnProperty.call(err, 'cnfrmPwdErr') ? err.cnfrmPwdErr : (''),
      })
    }
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  render() {
    const {
      newPwd,
      newPwdErr,
      cnfrmPwd,
      cnfrmPwdErr,
    } = this.state
    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          <Logo className={styles.logo} />
        </div>
        <form className={styles.form}>
          <h3 className={styles.header}> Change Password </h3>
          <div className={styles.newPassword}>
            <TextField
              type="password"
              name="newPwd"
              value={newPwd}
              placeholder="New Password"
              length="stretch"
              error={newPwdErr}
              onChange={value => this.handleChange('newPwd', value)}
            />
          </div>
          <div className={styles.cnfrmPassword}>
            <TextField
              type="password"
              name="cnfrmPwd"
              value={cnfrmPwd}
              placeholder="Confirm Password"
              length="stretch"
              error={cnfrmPwdErr}
              onChange={value => this.handleChange('cnfrmPwd', value)}
            />
          </div>
          {this.handleStatus()}
          <Button length="long" onClick={this.handleSubmit}> Reset Password </Button>
        </form>
      </div>
    )
  }
}

PasswordResetPage.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string,
    }),
  }).isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
}

export default PasswordResetPage
