import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import SecureConfirmModal from '../confirm-modal/SecureConfirmModal'
import { getUserProfile, updateEmail } from '../../../state/ducks/self/actions'

import styles from './SecurityPage.module.scss'

class SecurityPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isEditingEmail: false,
      isEmailValid: false,
      emailEditing: '',
      showConfirmModal: false,
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

  handleChangeEmail = (value) => {
    // TODO: Add validation
    this.setState({ emailEditing: value })
  }

  handleSubmitEmail = () => {
    // TODO: Check if email is valid
    const { emailEditing } = this.state
    const { updateEmailConnect } = this.props
    updateEmailConnect(emailEditing)
  }

  render() {
    const {
      user: {
        email,
        isEmailUpdating,
      },
    } = this.props
    const {
      isEditingEmail,
      emailEditing,
      showConfirmModal,
    } = this.state

    return (
      <div className={styles.main}>
        <header className={styles.inputHeader}>
          <h3>Email</h3>
          {
            isEmailUpdating
              ? <span className={`text--sub2 ${styles.status}`}>Updating email...</span>
              : ''
          }
        </header>
        <div className={`input-row ${styles.inputRow}`}>
          <span>Email</span>
          <TextField
            type="email"
            name="email"
            value={isEditingEmail ? emailEditing : email}
            placeholder="Email"
            length="stretch"
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
                    isDisabled={isEmailUpdating || emailEditing === ''}
                  >
                    Save
                  </Button>
                  <Button
                    appearance="outline"
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
        <SecureConfirmModal
          show={showConfirmModal}
          messageTitle={isEditingEmail ? 'Confirm your identity to update email' : ''}
          actionButtonName={isEditingEmail ? 'Update email' : ''}
          onSubmit={() => {
            if (isEditingEmail) {
              this.handleSubmitEmail()
              this.toggleEditingEmail()
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
  }).isRequired,
  getUserProfileConnect: PropTypes.func.isRequired,
  updateEmailConnect: PropTypes.string.isRequired,
}

const mapStateToProps = (state) => ({
  user: state.self.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateEmailConnect: updateEmail,
}

export default connect(mapStateToProps, mapDispatchToProps)(SecurityPage)
