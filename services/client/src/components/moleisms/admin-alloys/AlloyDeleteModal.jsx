import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'
import TextField from '../../elements/textfield'

import styles from './AlloyDeleteModal.module.scss'


class AlloyDeleteModal extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { passwordValid: false }
  }

  render() {
    const { show, onClose, onConfirm } = this.props
    const { passwordValid } = this.state

    return (
      <Modal show={show} className={styles.modal} withCloseIcon onClose={onClose}>
        <div className={styles.content}>
          <span className={styles.textDisplay}>
            Are you sure you would like to delete this alloy?
          </span>

          <div className={styles.passwordConfirm}>
            <span>
              Please enter your password to confirm this.
            </span>
            <TextField
              onChange={() => console.log('Text field change.')}
              type="password"
              name="confirmGlobalAlloyDelete"
              placeholder="Password..."
              length="stretch"
            />

          </div>

          <div className={styles.buttonGroup}>
            <Button
              name="cancelDelete"
              type="button"
              appearance="outline"
              length="long"
              onClick={onClose}
            >
              CANCEL
            </Button>
            <Button
              name="confirmDelete"
              appearance="text"
              length="long"
              color="dangerous"
              onClick={onConfirm}
              isDisabled={!passwordValid}
            >
              Confirm Delete
            </Button>
          </div>
        </div>
      </Modal>
    )
  }
}

AlloyDeleteModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
}

export default AlloyDeleteModal
