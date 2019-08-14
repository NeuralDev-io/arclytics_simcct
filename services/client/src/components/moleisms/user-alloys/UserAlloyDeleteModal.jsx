import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import Modal from '../../elements/modal'

import styles from './UserAlloyDeleteModal.module.scss'


// eslint-disable-next-line react/prefer-stateless-function
class UserAlloyDeleteModal extends Component {
  // eslint-disable-next-line no-useless-constructor
  constructor(props) {
    super(props)
  }

  render() {
    const { show, onClose, onConfirm } = this.props

    return (
      <Modal show={show} className={styles.modal} withCloseIcon onClose={onClose}>
        <div className={styles.content}>
          <span className={styles.textDisplay}>
            Are you sure you would like to delete this alloy?
          </span>

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
            >
              Confirm Delete
            </Button>
          </div>
        </div>
      </Modal>
    )
  }
}

UserAlloyDeleteModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
}

export default UserAlloyDeleteModal
