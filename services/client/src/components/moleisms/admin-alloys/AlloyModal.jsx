/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Modal to create global alloys
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Modal from '../../elements/modal'
import TextField from '../../elements/textfield'
import PeriodicTable from '../../elements/periodic-table'
import { PERIODIC_TABLE_DATA } from '../../../utils/alloys'
import Button from '../../elements/button'
import { validate } from '../../../utils/validator'
import { constraints } from './utils/constraints'

import styles from './AlloyModal.module.scss'

class AlloyModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      error: {
        name: '',
        compositions: {},
      },
    }
  }

  handleToggleElement = (number, newElements) => {
    // find data of this element
    const element = PERIODIC_TABLE_DATA.find(elem => elem.number === number)

    const { alloy, onChange } = this.props
    // if this element is one of the current elements
    if (!newElements.includes(number)) {
      // remove element from current compositions
      const newComp = alloy.compositions.filter(elem => elem.name !== element.name)
      onChange({
        ...alloy,
        compositions: newComp,
      })
    } else {
      // else add element to current compositions
      const newComp = alloy.compositions
      newComp.push({
        name: element.name,
        symbol: element.symbol,
        weight: 0,
      })
      onChange({
        ...alloy,
        compositions: newComp,
      })
    }
  }

  handleCompWeightChange = (symbol, value) => {
    const { alloy, onChange } = this.props
    const { error: { compositions } } = this.state

    const newComp = [...alloy.compositions]
    const idx = newComp.findIndex(elem => elem.symbol === symbol)
    newComp[idx] = {
      ...newComp[idx],
      weight: value,
    }

    let err
    if (symbol === 'C') {
      err = validate(value, constraints.carbon)
    } else err = validate(value, constraints.weight)
    if (err !== undefined) {
      this.setState(state => ({
        error: {
          ...state.error,
          compositions: {
            ...state.error.compositions,
            [symbol]: err,
          },
        },
      }))
    } else {
      const newCompError = { ...compositions }
      delete newCompError[symbol]
      this.setState(state => ({ error: { ...state.error, compositions: newCompError } }))
    }

    onChange({
      ...alloy,
      compositions: newComp,
    })
  }

  handleNameChange = (value) => {
    const { alloy, onChange } = this.props
    const err = validate(value, constraints.name)
    if (err !== undefined) {
      this.setState(state => ({
        error: {
          ...state.error,
          name: err,
        },
      }))
    } else {
      this.setState(state => ({
        error: {
          ...state.error,
          name: '',
        },
      }))
    }

    onChange({
      ...alloy,
      name: value,
    })
  }

  handleSaveAlloy = () => {
    const { alloy, onSave } = this.props

    const alloyComp = alloy.compositions.map(a => ({
      symbol: a.symbol,
      weight: parseFloat(a.weight),
    }))
    onSave({
      name: alloy.name,
      compositions: alloyComp,
    })
  }

  renderElements = () => {
    const { alloy } = this.props
    const { error } = this.state

    if (alloy.compositions.length === 0) {
      return <span className={styles.info}>Choose an element to start</span>
    }
    return alloy.compositions.map(({ symbol, weight }) => {
      const element = PERIODIC_TABLE_DATA.find(e => e.symbol === symbol)
      return (
        <div key={symbol} className={`input-row ${styles.element}`}>
          <span>{element.name}</span>
          <TextField
            name={element.name}
            value={weight}
            length="short"
            onChange={val => this.handleCompWeightChange(element.symbol, val)}
            error={error.compositions[element.symbol]}
          />
        </div>
      )
    })
  }

  render() {
    const { show, onClose, alloy } = this.props
    const { error } = this.state

    // get compositions from props and add fundamental elements if compositions is empty
    const { compositions = [] } = alloy

    // generate an elements array for PeriodicTable
    const elements = compositions.map((elem) => {
      const element = PERIODIC_TABLE_DATA.find(e => e.symbol === elem.symbol)
      return element.number
    })

    return (
      <Modal show={show} className={styles.modal} onClose={onClose} withCloseIcon>
        <div className={styles.periodic}>
          <PeriodicTable elements={elements} onToggleElement={this.handleToggleElement} />
        </div>
        <div className={styles.content}>
          <div>
            <div className={`input-col ${styles.name}`}>
              <h6>Alloy name</h6>
              <TextField
                onChange={val => this.handleNameChange(val)}
                type="text"
                name="name"
                placeholder="Alloy name..."
                length="stretch"
                value={alloy.name}
                error={error.name}
              />
            </div>
            <div className={styles.elementContainer}>
              {this.renderElements()}
            </div>
          </div>
          <Button
            type="button"
            onClick={this.handleSaveAlloy}
            className={styles.saveButton}
            length="long"
            isDisabled={alloy.name === '' || error.name !== '' || Object.keys(error.compositions).length !== 0}
          >
            SAVE
          </Button>
        </div>
      </Modal>
    )
  }
}

AlloyModal.propTypes = {
  alloy: PropTypes.shape({
    compositions: PropTypes.arrayOf(PropTypes.shape({
      symbol: PropTypes.string,
      weight: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    })),
    name: PropTypes.string,
    _id: PropTypes.string,
  }).isRequired,
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
}

export default AlloyModal
