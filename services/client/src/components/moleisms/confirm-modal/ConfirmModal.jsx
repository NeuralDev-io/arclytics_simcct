import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'
import TextField from '../../elements/textfield'
import { checkPassword } from '../../../api/AuthenticationHelper'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './SecureConfirmModal.module.scss'

class ConfirmModal extends Component {

  handleClose = () => {
    const { onClose } = this.props
    onClose()
  }

  handleSubmit = (e) => {
    e.preventDefault()
    const{ onSubmit } = this.props=
    onSubmit()
  }

  render() {
    const {
      show,
      messageTitle,
      actionButtonName,
    } = this.props

    return (
      <Modal show={show} className={`${styles.modal} ${styles.className}`} withCloseIcon onClose={this.handleClose}>
        <form className={styles.content} onSubmit={this.handleSubmit}>
          <div className={styles.header}>
            <h6> {messageTitle} </h6>
          </div>
          <div className={styles.buttonGroup}>
            <Button
              type="submit"
              name="confirmDelete"
              length="long"
            >
              Confirm
            </Button>
            <Button
              name="cancelDelete"
              type="button"
              appearance="outline"
              length="long"
              onClick={this.handleClose}
            >
              CANCEL
            </Button>

          </div>
        </form>
      </Modal>
    )
  }
}

ConfirmModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  successMessage: PropTypes.string,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(null, mapDispatchToProps)(ConfirmModal)
