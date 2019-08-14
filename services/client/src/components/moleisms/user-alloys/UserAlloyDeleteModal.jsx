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
    const { confirm } = this.props

    this.state = { confirm: false }
  }

  render() {
    const { show, onClose } = this.props
    const { confirm } = this.state

    return (
      <Modal show={show} className={styles.modal}>
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
              onClick={() => this.setState({ confirm: true })}
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
  confirm: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default UserAlloyDeleteModal
