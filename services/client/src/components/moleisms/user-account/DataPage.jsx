import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Button from '../../elements/button'
import { SecureConfirmModal } from '../confirm-modal'
import { deleteAccount, downloadAccountData } from '../../../state/ducks/self/actions'

import styles from './DataPage.module.scss'

class DataPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showConfirmModal: false,
      showDownloadConfirmModal: false,
    }
  }

  toggleConfirmModal = () => {
    this.setState(({ showConfirmModal }) => ({ showConfirmModal: !showConfirmModal }))
  }

  toggleDownloadConfirmModal = () => {
    this.setState(({ showDownloadConfirmModal }) => ({
      showDownloadConfirmModal: !showDownloadConfirmModal,
    }))
  }

  handleDeleteAccount = () => {
    const { deleteAccountConnect } = this.props
    deleteAccountConnect()
    this.toggleConfirmModal()
  }

  handleDownloadData = () => {
    const { downloadAccountDataConnect } = this.props
    downloadAccountDataConnect()
      .then((res) => {
        console.log(res)
      })
  }

  render() {
    const { isDeleting, isLoadingAccountData } = this.props
    const { showConfirmModal, showDownloadConfirmModal } = this.state
    return (
      <div className={styles.main}>
        <h3>Download your Arclytics SimCCT data</h3>
        <p className={styles.downloadP}>Download this data to your device.</p>
        <Button
          appearance="outline"
          length="long"
          onClick={this.toggleDownloadConfirmModal}
          isDisabled={isLoadingAccountData}
          className={`${styles.btn}`}
        >
          {
            isLoadingAccountData
              ? 'Collecting account data...'
              : 'Request data'
          }
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
        <SecureConfirmModal
          show={showDownloadConfirmModal}
          messageTitle="Please confirm your identiy to request account data"
          actionButtonName="Request data"
          onSubmit={this.handleDownloadData}
          onClose={this.toggleDownloadConfirmModal}
        />
      </div>
    )
  }
}

DataPage.propTypes = {
  isDeleting: PropTypes.bool.isRequired,
  isLoadingAccountData: PropTypes.bool.isRequired,
  deleteAccountConnect: PropTypes.func.isRequired,
  downloadAccountDataConnect: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => ({
  isDeleting: state.self.user.isDeleting,
  isLoadingAccountData: state.self.user.isLoadingAccountData,
})

const mapDispatchToProps = {
  deleteAccountConnect: deleteAccount,
  downloadAccountDataConnect: downloadAccountData,
}

export default connect(mapStateToProps, mapDispatchToProps)(DataPage)
