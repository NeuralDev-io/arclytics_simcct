import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'
import TextField from '../../elements/textfield'
import { checkPassword } from '../../../api/AuthenticationHelper'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './SecureConfirmModal.module.scss'

class SecureConfirmModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      password: '',
    }
  }

  handleSubmit = (e) => {
    e.preventDefault()
    const { addFlashToastConnect, onSubmit } = this.props
    const { password } = this.state
    checkPassword(password)
      .then((isValid) => {
        if (isValid) {
          onSubmit()
          this.setState({ password: '' })
        } else {
          addFlashToastConnect({
            message: 'Incorrect password',
            options: { variant: 'error' },
          }, true)
        }
      })
  }

  handleClose = () => {
    const { onClose } = this.props
    this.setState({ password: '' })
    onClose()
  }

  render() {
    const {
      show,
      messageTitle,
      messageBody,
      actionButtonName,
      isDangerous,
    } = this.props
    const { password } = this.state

    return (
      <Modal show={show} className={`${styles.modal} ${styles.className}`} withCloseIcon onClose={this.handleClose}>
        <form className={styles.content} onSubmit={this.handleSubmit}>
          <div className={styles.header}>
            <h6 className={isDangerous ? styles.dangerous : ''}>{messageTitle}</h6>
            <p>{messageBody}</p>
          </div>
          <TextField
            onChange={val => this.setState({ password: val })}
            type="password"
            name="confirmGlobalAlloyDelete"
            placeholder="Password..."
            length="stretch"
            value={password}
          />
          <div className={styles.buttonGroup}>
            <Button
              name="cancelDelete"
              type="button"
              appearance="outline"
              length="long"
              onClick={this.handleClose}
            >
              CANCEL
            </Button>
            <Button
              type="submit"
              name="confirmDelete"
              appearance="text"
              // length="long"
              className={styles.confirmBtn}
              color={isDangerous ? 'dangerous' : 'default'}
              isDisabled={password === ''}
            >
              {actionButtonName}
            </Button>
          </div>
        </form>
      </Modal>
    )
  }
}

SecureConfirmModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  messageTitle: PropTypes.string,
  messageBody: PropTypes.string,
  actionButtonName: PropTypes.string,
  addFlashToastConnect: PropTypes.func.isRequired,
  isDangerous: PropTypes.bool,
}

SecureConfirmModal.defaultProps = {
  actionButtonName: 'Confirm',
  messageTitle: 'Please confirm',
  messageBody: 'Please enter password to confirm.',
  isDangerous: false,
}

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(null, mapDispatchToProps)(SecureConfirmModal)
