import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'
import TextField from '../../elements/textfield'

import styles from './AlloyDeleteModal.module.scss'


class AlloyDeleteModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      passwordValid: false,
      password: '',
    }
  }

  render() {
    const {
      alloyId,
      show,
      onClose,
      onConfirm,
    } = this.props
    const { password, passwordValid } = this.state

    return (
      <Modal show={show} className={styles.modal} withCloseIcon onClose={onClose}>
        <form className={styles.content} onSubmit={() => onConfirm(alloyId)}>
          <span className={styles.textDisplay}>
            Are you sure you would like to delete this alloy?
          </span>
          <div className={styles.passwordConfirm}>
            <span>
              Please enter your password to confirm this.
            </span>
            <TextField
              onChange={val => this.setState({ password: val })}
              type="password"
              name="confirmGlobalAlloyDelete"
              placeholder="Password..."
              length="stretch"
              value={password}
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
              type="submit"
              name="confirmDelete"
              appearance="text"
              length="long"
              color="dangerous"
              onClick={() => onConfirm(alloyId)}
              isDisabled={!passwordValid}
            >
              Confirm Delete
            </Button>
          </div>
        </form>
      </Modal>
    )
  }
}

AlloyDeleteModal.propTypes = {
  alloyId: PropTypes.string.isRequired,
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
}

export default AlloyDeleteModal
