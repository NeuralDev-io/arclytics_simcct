/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Load button with AttachModal to load a simulation from a file
 *
 * @version 1.0.0
 * @author Dalton Le
 */
/* eslint-disable react/jsx-props-no-spreading */
import React, { Component } from 'react'
// noinspection ES6CheckImport
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUpload } from '@fortawesome/pro-light-svg-icons/faUpload'
import Button from '../../elements/button'
import FileInput from '../../elements/file-input/FileInput'
import { AttachModal } from '../../elements/modal'
import { loadSimFromFile } from '../../../state/ducks/sim/actions'
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
    const { loadSimFromFileConnect, addFlashToastConnect } = this.props
    const file = e.target.files[0]

    if (file === null || file === undefined) return

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
    reader.onload = (ev) => {
      let sim
      try {
        const fileText = ev.target.result
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
      loadSimFromFileConnect(sim)
      this.setState({ filename: file.name })
      addFlashToastConnect({
        message: 'File imported successfully',
        options: { variant: 'success' },
      }, true)
      setTimeout(this.handleCloseModal, 500)
    }

    reader.readAsText(file)
    e.target.value = null
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
          IconComponent={props => <FontAwesomeIcon icon={faUpload} {...props} />}
        >
          LOAD
        </Button>
        <div className={styles.modal}>
          <h4>Import simulation</h4>
          <FileInput
            name="import_simulation"
            Icon={props => <FontAwesomeIcon icon={faUpload} {...props} />}
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
  loadSimFromFileConnect: PropTypes.func.isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  loadSimFromFileConnect: loadSimFromFile,
  addFlashToastConnect: addFlashToast,
}

export default connect(null, mapDispatchToProps)(LoadSimButton)
