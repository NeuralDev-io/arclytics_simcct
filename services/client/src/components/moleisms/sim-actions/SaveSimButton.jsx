/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Button to save a simulation either to account/to a file.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import FileSaver from 'file-saver'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSave } from '@fortawesome/pro-light-svg-icons/faSave'
import { faFile } from '@fortawesome/pro-light-svg-icons/faFile'
import Button from '../../elements/button'
import Portal from '../../elements/portal'
import { AttachModal } from '../../elements/modal'
import ReportDownloadLink from '../pdf-export'
import { Equilibrium } from '../charts'
import { buttonize } from '../../../utils/accessibility'
import { saveSimulation } from '../../../state/ducks/self/actions'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './SaveSimButton.module.scss'

class SaveSimButton extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
      showDownload: false,
    }
  }

  handleShowModal = () => this.setState({ visible: true })

  handleCloseModal = () => this.setState({ visible: false })

  handleShowDownloadLink = () => {
    setTimeout(() => {
      this.setState({ showDownload: true })
    }, 100)
  }

  handleCloseDownloadLink = () => this.setState({ showDownload: false })

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
    const { visible, showDownload } = this.state

    // this is a bit hacky, we're checking if a new simulation is in progress while
    // showDownload is still true --> set showDownload to false so the next time
    // it's true, the ReportDownloadLink component is re-rendered and will generate
    // a new PDF report.
    if (!isSimulated && showDownload) this.setState({ showDownload: false })

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
          IconComponent={props => <FontAwesomeIcon icon={faSave} {...props} />}
          isDisabled={!isSimulated || !isAuthenticated}
        >
          SAVE
        </Button>
        <div className={styles.optionList}>
          <h4>Save simulation</h4>
          <div className={styles.option} {...buttonize(this.saveSim)}>
            <FontAwesomeIcon icon={faSave} className={styles.icon} />
            <span>Save to your account</span>
          </div>
          <div className={styles.option} {...buttonize(this.saveSimAsFile)}>
            <FontAwesomeIcon icon={faFile} className={styles.icon} />
            <span>Save to file</span>
          </div>
          <h6 className={styles.divider}>
            <span>or</span>
          </h6>
          <div className={styles.download}>
            <span>Download the simulation as a .PDF report</span>
            {
              !showDownload
                ? (
                  <Button
                    appearance="outline"
                    length="long"
                    onClick={this.handleShowDownloadLink}
                    isDisabled={!isSimulated || !isAuthenticated}
                  >
                    Generate report
                  </Button>
                )
                : (
                  <ReportDownloadLink
                    onFinish={this.handleCloseModal}
                    onError={this.handleCloseDownloadLink}
                  />
                )
            }
          </div>
          {
            visible
              ? (
                <Portal to={document.getElementById('temp-container')}>
                  <div className={styles.equiChart} id="equi_chart">
                    <Equilibrium />
                  </div>
                </Portal>
              )
              : ''
          }
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
