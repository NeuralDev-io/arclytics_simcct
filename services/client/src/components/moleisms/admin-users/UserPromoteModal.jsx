import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'
import TextField from '../../elements/textfield'
import { checkPassword } from '../../../api/AuthenticationHelper'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './UserPromoteModal.module.scss'

class UserPromoteModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      position: '',
      password: '',
    }
  }

  handleSubmit = (e, alloyId) => {
    e.preventDefault()
    const { addFlashToastConnect, onSubmit, email } = this.props
    const { password, position } = this.state
    checkPassword(password)
      .then((isValid) => {
        if (isValid) {
          onSubmit(email, position)
          this.setState({ position: '', password: '' })
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
    this.setState({ position: '', password: '' })
    onClose()
  }

  render() {
    const {
      show,
      messageTitle,
      actionButtonName,
    } = this.props
    const { password, position } = this.state

    return (
      <Modal show={show} className={`${styles.modal} ${styles.className}`} withCloseIcon onClose={this.handleClose}>
        <form className={styles.content} onSubmit={this.handleSubmit}>
          <div className={styles.header}>
            <h6> {messageTitle} </h6>
            <span>Assign a position to the user.</span>
            <br/>
            <span>Enter your password to confirm.</span>
          </div>
          <TextField
            onChange={val => this.setState({ position: val })}
            type="text"
            name="position"
            placeholder="Position Name..."
            length="stretch"
            className={styles.positionTextField}
            value={position}
          />
          <TextField
            onChange={val => this.setState({ password: val })}
            type="password"
            name="passwordPromoteUser"
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
              length="long"
              isDisabled={password === '' || position === ''}
            >
              {actionButtonName}
            </Button>
          </div>
        </form>
      </Modal>
    )
  }
}

UserPromoteModal.propTypes = {
  email: PropTypes.string.isRequired,
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  successMessage: PropTypes.string,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(null, mapDispatchToProps)(UserPromoteModal)
