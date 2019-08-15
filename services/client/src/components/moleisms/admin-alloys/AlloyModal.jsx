import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Modal from '../../elements/modal'
import TextField from '../../elements/textfield'
import PeriodicTable, { PeriodicTableData } from '../../elements/periodic-table'

import styles from './AlloyModal.module.scss'
import Button from '../../elements/button';

class AlloyModal extends Component {
  constructor(props) {
    super(props)
    const { compositions = [], name } = this.props
    const elements = []
    const stateComp = []
    compositions.forEach((elem) => {
      const element = PeriodicTableData.find(e => e.symbol === elem.symbol)
      elements.push(element.number)
      stateComp.push({
        name: element.name,
        symbol: element.symbol,
        weight: elem.weight || 0,
      })
    })
    this.state = {
      name,
      elements,
      compositions: stateComp,
    }
  }

  handleToggleElement = (number, newElements) => {
    // find data of this element
    const element = PeriodicTableData.find(elem => elem.number === number)

    const { elements } = this.state
    // if this element is one of the current elements
    if (elements.includes(number)) {
      // remove element from current compositions
      this.setState(prevState => ({
        elements: newElements,
        compositions: prevState.compositions.filter(elem => elem.name !== element.name),
      }))
    } else {
      // else add element to current compositions
      this.setState((prevState) => {
        const newComp = prevState.compositions
        newComp.push({
          name: element.name,
          symbol: element.symbol,
          weight: 0,
        })
        return ({
          elements: newElements,
          compositions: newComp,
        })
      })
    }
  }

  handleCompWeightChange = (name, value) => {
    this.setState((prevState) => {
      const newCompositions = [...prevState.compositions]
      const idx = newCompositions.findIndex(elem => elem.name === name)
      newCompositions[idx] = {
        ...newCompositions[idx],
        weight: value,
      }
      return ({ compositions: newCompositions })
    })
  }

  handleSaveAlloy = () => {
    const { compositions, name } = this.state
    const { onSave } = this.props

    const alloyComp = compositions.map(a => ({
      symbol: a.symbol,
      weight: a.weight,
    }))
    onSave({
      name,
      compositions: alloyComp,
    })
  }

  renderElements = () => {
    const { compositions } = this.state
    if (compositions.length === 0) {
      return <span className={styles.info}>Choose an element to start</span>
    }
    return compositions.map(({ name, weight }) => (
      <div key={name} className={`input-row ${styles.element}`}>
        <span>{name}</span>
        <TextField
          name={name}
          value={weight}
          length="short"
          onChange={val => this.handleCompWeightChange(name, val)}
        />
      </div>
    ))
  }

  render() {
    const { elements, name } = this.state
    const { show, onClose } = this.props
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
                onChange={val => this.setState({ name: val })}
                type="text"
                name="name"
                placeholder="Alloy name..."
                length="stretch"
                value={name}
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
          >
            SAVE
          </Button>
        </div>
      </Modal>
    )
  }
}

AlloyModal.propTypes = {
  compositions: PropTypes.arrayOf(PropTypes.shape({
    symbol: PropTypes.string,
    weight: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  })).isRequired,
  name: PropTypes.string.isRequired,
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
}

export default AlloyModal
