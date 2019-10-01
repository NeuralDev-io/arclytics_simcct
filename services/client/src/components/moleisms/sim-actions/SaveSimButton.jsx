import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import FileSaver from 'file-saver'
import SaveIcon from 'react-feather/dist/icons/save'
import ServerIcon from 'react-feather/dist/icons/server'
import FileIcon from 'react-feather/dist/icons/file'
import Button from '../../elements/button'
import { AttachModal } from '../../elements/modal'
import { buttonize } from '../../../utils/accessibility'
import { saveSimulation } from '../../../state/ducks/self/actions'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './SaveSimButton.module.scss'

class SaveSimButton extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
    }
  }

  handleShowModal = () => this.setState({ visible: true })

  handleCloseModal = () => this.setState({ visible: false })

  saveSim = () => {
    const { saveSimulationConnect, addFlashToastConnect, sim: { configurations } } = this.props
    if (Object.keys(configurations.error).length !== 0) {
      addFlashToastConnect({
        message: 'Cannot save invalid configurations',
        options: { variant: 'error' },
      }, true)
    } else {
      saveSimulationConnect()
    }
    this.handleCloseModal()
  }

  saveSimAsFile = () => {
    const {
      sim: {
        configurations: {
          error,
          ...otherConfigs
        },
        alloys: {
          parentError,
          isLoading,
          ...otherAlloys
        },
        results: {
          cctIndex,
          ...otherResults
        },
      },
    } = this.props
    const savedSim = {
      configurations: otherConfigs,
      alloys: otherAlloys,
      results: otherResults,
    }
    const blob = new Blob([JSON.stringify(savedSim)], { type: 'text/plain;charset=utf-8' })
    FileSaver.saveAs(blob, `arc_sim_${new Date().toISOString()}.json`)
    this.handleCloseModal()
  }

  render() {
    const { isSimulated, isAuthenticated } = this.props
    const { visible } = this.state

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
          IconComponent={props => <SaveIcon {...props} />}
          isDisabled={!isSimulated || !isAuthenticated}
        >
          SAVE
        </Button>
        <div className={styles.optionList}>
          <h4>Save simulation</h4>
          <div className={styles.option} {...buttonize(this.saveSim)}>
            <ServerIcon className={styles.icon} />
            <span>Save to your account</span>
          </div>
          <div className={styles.option} {...buttonize(this.saveSimAsFile)}>
            <FileIcon className={styles.icon} />
            <span>Save to file</span>
          </div>
        </div>
      </AttachModal>
    )
  }
}

SaveSimButton.propTypes = {
  isSimulated: PropTypes.bool.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  // props from connect()
  saveSimulationConnect: PropTypes.func.isRequired,
  sim: PropTypes.shape({
    configurations: PropTypes.shape({
      error: PropTypes.shape({}),
    }),
    results: PropTypes.shape({
      cctIndex: PropTypes.number,
    }),
    alloys: PropTypes.shape({
      parentError: PropTypes.shape({}),
      isLoading: PropTypes.bool,
    }),
  }).isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  sim: {
    results: state.sim.results,
    configurations: state.sim.configurations,
    alloys: state.sim.alloys,
  },
})

const mapDispatchToProps = {
  saveSimulationConnect: saveSimulation,
  addFlashToastConnect: addFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(SaveSimButton)
