import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Button from '../../elements/button'
import { SecureConfirmModal } from '../confirm-modal'
import { deleteAccount } from '../../../state/ducks/self/actions'

import styles from './DataPage.module.scss'

class DataPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showConfirmModal: false,
    }
  }

  componentDidMount = () => {
  }

  toggleConfirmModal = () => {
    this.setState(({ showConfirmModal }) => ({ showConfirmModal: !showConfirmModal }))
  }

  handleDeleteAccount = () => {
    const { deleteAccountConnect } = this.props
    deleteAccountConnect()
    this.toggleConfirmModal()
  }

  render() {
    const { isDeleting } = this.props
    const { showConfirmModal } = this.state
    return (
      <div className={styles.main}>
        <h3>Download your Arclytics SimCCT data</h3>
        <p className={styles.downloadP}>Download this data to your device.</p>
        <Button
          appearance="outline"
          length="long"
          onClick={() => {}}
          className={`${styles.btn}`}
        >
          Request data
        </Button>
        <h3>Delete your account</h3>
        <div className={styles.deleteGroup}>
          <p>
            Delete your account will also delete your data from our system.
          </p>
          <Button
            appearance="text"
            color="dangerous"
            className={styles.deleteButton}
            onClick={this.toggleConfirmModal}
            isDisabled={isDeleting}
          >
            {
              !isDeleting
                ? 'Delete your account'
                : 'Deleting account'
            }
          </Button>
        </div>
        <SecureConfirmModal
          show={showConfirmModal}
          messageTitle="Are you sure you want to do this?"
          messageBody={
            'We will immediately delete all your saved simulations, personal alloys'
            + 'and personal information.'
            + ' You will no longer be able to log in using this account.'
          }
          actionButtonName="Delete this account"
          onSubmit={this.handleDeleteAccount}
          onClose={this.toggleConfirmModal}
          isDangerous
        />
      </div>
    )
  }
}

DataPage.propTypes = {
  isDeleting: PropTypes.bool.isRequired,
  deleteAccountConnect: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => ({
  isDeleting: state.self.user.isDeleting,
})

const mapDispatchToProps = {
  deleteAccountConnect: deleteAccount,
}

export default connect(mapStateToProps, mapDispatchToProps)(DataPage)
