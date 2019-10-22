/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Modal to enter a name before the user saves an alloy from CompSidebar
 * to their personal database.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import { createUserAlloy } from '../../../state/ducks/alloys/actions'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './SaveAlloyModal.module.scss'

class SaveAlloyModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      savedAlloy: '',
    }
  }

  handleAlloyNameChange = name => this.setState({ savedAlloy: name })

  handleSaveAlloy = (e) => {
    e.preventDefault()
    const { savedAlloy } = this.state
    const {
      activeAlloy,
      createUserAlloyConnect,
      addFlashToastConnect,
      handleClose,
    } = this.props
    createUserAlloyConnect({
      name: savedAlloy,
      compositions: activeAlloy.compositions,
    })
      .then(() => {
        handleClose()
        this.setState({ savedAlloy: '' })
        addFlashToastConnect({
          message: 'Alloy saved',
          options: { variant: 'success' },
        }, true)
      })
  }

  render() {
    const { savedAlloy } = this.state
    const { handleClose } = this.props

    return (
      <form onSubmit={this.handleSaveAlloy} className={styles.form}>
        <div className={`input-col ${styles.inputContainer}`}>
          <h6>Choose a name to for this alloy</h6>
          <TextField
            type="text"
            name="alloyName"
            placeholder="Enter alloy name"
            onChange={val => this.handleAlloyNameChange(val)}
            value={savedAlloy}
            length="stretch"
          />
        </div>
        <div className={styles.buttons}>
          <Button
            onClick={this.handleSaveAlloy}
            length="long"
            isDisabled={savedAlloy === undefined || savedAlloy === ''}
          >
            Save
          </Button>
          <Button
            onClick={handleClose}
            length="long"
            appearance="outline"
          >
            Cancel
          </Button>
        </div>
      </form>
    )
  }
}

SaveAlloyModal.propTypes = {
  handleClose: PropTypes.func.isRequired,
  // from connect()
  activeAlloy: PropTypes.shape({
    _id: PropTypes.string,
    name: PropTypes.string,
    compositions: PropTypes.arrayOf(PropTypes.shape({
      symbol: PropTypes.string,
      weight: PropTypes.number,
    })),
  }).isRequired,
  createUserAlloyConnect: PropTypes.func.isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  activeAlloy: state.sim.alloys.parent,
})

const mapDispatchToProps = {
  createUserAlloyConnect: createUserAlloy,
  addFlashToastConnect: addFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(SaveAlloyModal)
