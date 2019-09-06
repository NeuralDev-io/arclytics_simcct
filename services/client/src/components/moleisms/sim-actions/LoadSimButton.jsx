import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withSnackbar } from 'notistack'
import UploadIcon from 'react-feather/dist/icons/upload'
import Button from '../../elements/button'
import FileInput from '../../elements/file-input/FileInput'
import { AttachModal } from '../../elements/modal'
import { loadSim } from '../../../state/ducks/sim/actions'

import styles from './LoadSimButton.module.scss'

class LoadSimButton extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
      filename: '',
    }
  }

  handleShowModal = () => this.setState({ visible: true })

  handleCloseModal = () => this.setState({ visible: false })

  handleFileInputChange = (e) => {
    const { enqueueSnackbar, closeSnackbar, loadSimConnect } = this.props
    const file = e.target.files[0]

    // check file size
    if (file.size > 100000) {
      enqueueSnackbar('File size too large', {
        variant: 'error',
        action: key => (
          <Button
            appearance="text"
            className="snackbar__button"
            onClick={() => closeSnackbar(key)}
          >
            Dismiss
          </Button>
        ),
      })
      this.handleCloseModal()
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      let sim
      try {
        const fileText = e.target.result
        sim = JSON.parse(fileText)
      } catch (err) {
        console.error(err)
        enqueueSnackbar('Something went wrong', {
          variant: 'error',
          action: key => (
            <Button
              appearance="text"
              className="snackbar__button"
              onClick={() => closeSnackbar(key)}
            >
              Dismiss
            </Button>
          ),
        })
        this.handleCloseModal()
        return
      }

      // TODO: validate sim schema

      // load simulations
      loadSimConnect(sim)
      this.setState({ filename: file.name })
      enqueueSnackbar('File imported successfully.', {
        variant: 'success',
        action: key => (
          <Button
            appearance="text"
            className="snackbar__button"
            onClick={() => closeSnackbar(key)}
          >
            Dismiss
          </Button>
        ),
      })
      setTimeout(this.handleCloseModal, 500)
    }

    reader.readAsText(file)
  }

  render() {
    const { visible, filename } = this.state

    return (
      <AttachModal
        visible={visible}
        handleClose={this.handleCloseModal}
        handleShow={this.handleShowModal}
        position="topRight"
        overlap
      >
        <Button
          appearance="outline"
          type="button"
          onClick={() => {}}
          IconComponent={props => <UploadIcon {...props} />}
        >
          LOAD
        </Button>
        <div className={styles.modal}>
          <h4>Import simulation</h4>
          <FileInput
            Icon={props => <UploadIcon {...props} />}
            onChange={this.handleFileInputChange}
            filename={filename}
          />
        </div>
      </AttachModal>
    )
  }
}

LoadSimButton.propTypes = {
  enqueueSnackbar: PropTypes.func.isRequired,
  closeSnackbar: PropTypes.func.isRequired,
  // props from connect()
  loadSimConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  loadSimConnect: loadSim,
}

export default withSnackbar(connect(null, mapDispatchToProps)(LoadSimButton))