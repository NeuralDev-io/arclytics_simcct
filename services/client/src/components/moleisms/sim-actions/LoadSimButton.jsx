import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import UploadIcon from 'react-feather/dist/icons/upload'
import Button from '../../elements/button'
import FileInput from '../../elements/file-input/FileInput'
import { AttachModal } from '../../elements/modal'
import { loadSim } from '../../../state/ducks/sim/actions'
import { addFlashToast } from '../../../state/ducks/toast/actions'

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
    const { loadSimConnect, addFlashToastConnect } = this.props
    const file = e.target.files[0]

    // check file size
    if (file.size > 200000) {
      addFlashToastConnect({
        message: 'File size too large',
        options: { variant: 'error' },
      }, true)
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
        addFlashToastConnect({
          message: 'Something went wrong',
          options: { variant: 'error' },
        }, true)
        this.handleCloseModal()
        return
      }

      // TODO: validate sim schema

      // load simulations
      loadSimConnect(sim)
      this.setState({ filename: file.name })
      addFlashToastConnect({
        message: 'File imported successfully',
        options: { variant: 'success' },
      }, true)
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
            name="import_simulation"
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
  // props from connect()
  loadSimConnect: PropTypes.func.isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  loadSimConnect: loadSim,
  addFlashToastConnect: addFlashToast,
}

export default connect(null, mapDispatchToProps)(LoadSimButton)
