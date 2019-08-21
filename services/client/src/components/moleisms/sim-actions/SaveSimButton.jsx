import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import SaveIcon from 'react-feather/dist/icons/save'
import ServerIcon from 'react-feather/dist/icons/server'
import FileIcon from 'react-feather/dist/icons/file'
import Button from '../../elements/button'
import { AttachModal } from '../../elements/modal'
import { buttonize } from '../../../utils/accessibility'
import { saveSimulation } from '../../../state/ducks/self/actions'

import styles from './SaveSimButton.module.scss'

const SaveSimButton = ({ isSessionInitialised, saveSimulationConnect }) => {
  return (
    <AttachModal position="topRight" overlap>
      <Button
        appearance="outline"
        type="button"
        onClick={() => {}}
        IconComponent={props => <SaveIcon {...props} />}
        isDisabled={!isSessionInitialised}
      >
        SAVE
      </Button>
      <div className={styles.optionList}>
        <h4>Save simulation</h4>
        <div className={styles.option} {...buttonize(saveSimulationConnect)}>
          <ServerIcon className={styles.icon} />
          <span>Save to your account</span>
        </div>
        <div className={styles.option}>
          <FileIcon className={styles.icon} />
          <span>Save to file</span>
        </div>
      </div>
    </AttachModal>
  )
}

SaveSimButton.propTypes = {
  isSessionInitialised: PropTypes.bool.isRequired,
  // props from connect()
  saveSimulationConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  saveSimulationConnect: saveSimulation,
}

export default connect(null, mapDispatchToProps)(SaveSimButton)
