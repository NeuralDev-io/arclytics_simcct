import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Button from '../../elements/button'
import Modal from '../../elements/modal/Modal'
import TextField from '../../elements/textfield'
import { checkPassword } from '../../../api/AuthenticationHelper'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './AlloyDeleteModal.module.scss'

class AlloyDeleteModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      password: '',
    }
  }

  handleSubmit = (e, alloyId) => {
    e.preventDefault()
    const { onConfirm, addFlashToastConnect } = this.props
    const { password } = this.state
    checkPassword(password)
      .then((isValid) => {
        if (isValid) {
          onConfirm(alloyId)
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
      alloyId,
      show,
    } = this.props
    const { password } = this.state

    return (
      <Modal show={show} className={styles.modal} withCloseIcon onClose={this.handleClose}>
        <form className={styles.content} onSubmit={e => this.handleSubmit(e, alloyId)}>
          <div className={styles.header}>
            <h6>Are you sure you want to delete this alloy?</h6>
            <span>Please enter password to confirm.</span>
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
              length="long"
              color="dangerous"
              isDisabled={password === ''}
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
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(null, mapDispatchToProps)(AlloyDeleteModal)
