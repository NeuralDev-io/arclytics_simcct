import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import SecureConfirmModal from '../confirm-modal/SecureConfirmModal'
import { getUserProfile, updateEmail, changePassword } from '../../../state/ducks/self/actions'
import { validate, validateGroup } from '../../../utils/validator'
import { constraints } from './utils/constraints'

import styles from './SecurityPage.module.scss'

class SecurityPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isEditingEmail: false,
      emailEditing: '',
      isEditingPassword: false,
      password: '',
      passwordConfirm: '',
      showConfirmModal: false,
      error: {
        email: '',
        password: '',
        passwordConfirm: '',
      },
    }
  }

  componentDidMount = () => {
    const { user: { isFetched }, getUserProfileConnect } = this.props
    if (!isFetched) {
      getUserProfileConnect()
    }
  }

  toggleConfirmModal = () => {
    this.setState(({ showConfirmModal }) => ({ showConfirmModal: !showConfirmModal }))
  }

  toggleEditingEmail = () => {
    this.setState(({ isEditingEmail }) => ({ isEditingEmail: !isEditingEmail }))
  }

  toggleEditingPassword = () => {
    this.setState(({ isEditingPassword, error }) => {
      if (isEditingPassword) {
        return {
          isEditingPassword: false,
          password: '',
          passwordConfirm: '',
          error: {
            ...error,
            passwordConfirm: '',
            password: '',
          },
        }
      }
      return {
        isEditingPassword: true,
      }
    })
  }

  handleChangeEmail = (value) => {
    const err = validate(value, constraints.email)
    if (err !== undefined) {
      // email is not valid
      this.setState(({ error }) => ({
        error: {
          ...error,
          email: err,
        },
        emailEditing: value,
      }))
      return
    }
    // email is valid
    this.setState(({ error }) => ({
      error: {
        ...error,
        email: '',
      },
      emailEditing: value,
    }))
  }

  handleSubmitEmail = () => {
    const { emailEditing } = this.state
    const { updateEmailConnect } = this.props
    updateEmailConnect(emailEditing)
  }

  handleChangePassword = (field, value) => {
    // check if this password is valid
    let err = validate(value, constraints.password)
    if (err !== undefined) {
      // password is not valid
      this.setState(({ error }) => ({
        error: {
          ...error,
          passwordConfirm: '',
          [field]: err,
        },
        [field]: value,
      }))
      return
    }

    // password is valid, now we check if they match
    const { password, passwordConfirm } = this.state
    const passwordTuple = { password, passwordConfirm }
    passwordTuple[field] = value
    err = validateGroup(passwordTuple, constraints.passwordMatch)
    if (err !== undefined) {
      // passwords don't match
      this.setState(({ error }) => ({
        error: {
          ...error,
          [field]: '',
          passwordConfirm: err,
        },
        [field]: value,
      }))
      return
    }

    // all good
    this.setState(({ error }) => ({
      error: {
        ...error,
        passwordConfirm: '',
        password: '',
      },
      [field]: value,
    }))
  }

  handleSubmitPassword = () => {
    const { changePasswordConnect } = this.props
    const { password, passwordConfirm } = this.state
    changePasswordConnect(password, passwordConfirm)
  }

  render() {
    const {
      user: {
        email,
        isEmailUpdating,
        isPasswordUpdating,
      },
    } = this.props
    const {
      isEditingEmail,
      emailEditing,
      isEditingPassword,
      password,
      passwordConfirm,
      showConfirmModal,
      error: {
        email: emailError,
        password: passwordError,
        passwordConfirm: passwordConfirmError,
      },
    } = this.state

    return (
      <div className={styles.main}>
        <header className={styles.inputHeader}>
          <h3 className={styles.heading}>Email</h3>
          {
            isEmailUpdating
              ? <span className={`text--sub2 ${styles.status}`}>Updating email...</span>
              : ''
          }
        </header>
        <div className={`input-row ${styles.inputRow}`}>
          <span>Email</span>
          <TextField
            type="text"
            name="email"
            value={isEditingEmail ? emailEditing : email}
            placeholder="Enter new email"
            length="stretch"
            error={emailError}
            isDisabled={!isEditingEmail}
            onChange={this.handleChangeEmail}
          />
        </div>
        <div className={styles.buttonGroup}>
          {
            isEditingEmail
              ? (
                <>
                  <Button
                    onClick={this.toggleConfirmModal}
                    length="long"
                    isDisabled={isEmailUpdating || emailEditing === '' || emailError !== ''}
                  >
                    Save
                  </Button>
                  <Button
                    appearance="outline"
                    length="long"
                    onClick={this.toggleEditingEmail}
                  >
                    Cancel
                  </Button>
                </>
              )
              : (
                <Button
                  onClick={this.toggleEditingEmail}
                  appearance="outline"
                  length="long"
                >
                  Change email
                </Button>
              )
          }
        </div>
        <header className={styles.inputHeader}>
          <h3 className={styles.heading}>Password</h3>
          {
            isPasswordUpdating
              ? <span className={`text--sub2 ${styles.status}`}>Updating password...</span>
              : ''
          }
        </header>
        <div className={styles.passwordGroup}>
          <div className={`input-row ${styles.inputRow}`}>
            <span>Enter new password</span>
            <TextField
              type="password"
              name="password"
              value={password}
              placeholder="New password"
              length="stretch"
              error={passwordError}
              isDisabled={!isEditingPassword}
              onChange={val => this.handleChangePassword('password', val)}
            />
          </div>
          <div className={`input-row ${styles.inputRow}`}>
            <span>Confirm new password</span>
            <TextField
              type="password"
              name="passwordConfirm"
              value={passwordConfirm}
              placeholder="Confirm new password"
              length="stretch"
              error={passwordConfirmError}
              isDisabled={!isEditingPassword}
              onChange={val => this.handleChangePassword('passwordConfirm', val)}
            />
          </div>
          <div className={styles.buttonGroup}>
            {
              isEditingPassword
                ? (
                  <>
                    <Button
                      onClick={this.toggleConfirmModal}
                      length="long"
                      isDisabled={
                        isPasswordUpdating || password === '' || passwordConfirm === ''
                        || passwordError !== '' || passwordConfirmError !== ''
                      }
                    >
                      Save
                    </Button>
                    <Button
                      appearance="outline"
                      length="long"
                      onClick={this.toggleEditingPassword}
                    >
                      Cancel
                    </Button>
                  </>
                )
                : (
                  <Button
                    onClick={this.toggleEditingPassword}
                    appearance="outline"
                    length="long"
                  >
                    Change password
                  </Button>
                )
            }
          </div>
        </div>
        <SecureConfirmModal
          show={showConfirmModal}
          messageTitle={isEditingEmail ? 'Confirm your identity to update email' : 'Confirm your identity to change password'}
          actionButtonName={isEditingEmail ? 'Update email' : 'Change password'}
          onSubmit={() => {
            if (isEditingEmail) {
              this.handleSubmitEmail()
              this.toggleEditingEmail()
            }
            if (isEditingPassword) {
              this.handleSubmitPassword()
              this.toggleEditingPassword()
            }
            this.toggleConfirmModal()
          }}
          onClose={this.toggleConfirmModal}
        />
      </div>
    )
  }
}

SecurityPage.propTypes = {
  user: PropTypes.shape({
    email: PropTypes.string,
    isFetched: PropTypes.bool,
    isEmailUpdating: PropTypes.bool,
    isPasswordUpdating: PropTypes.bool,
  }).isRequired,
  getUserProfileConnect: PropTypes.func.isRequired,
  updateEmailConnect: PropTypes.string.isRequired,
  changePasswordConnect: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => ({
  user: state.self.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateEmailConnect: updateEmail,
  changePasswordConnect: changePassword,
}

export default connect(mapStateToProps, mapDispatchToProps)(SecurityPage)
