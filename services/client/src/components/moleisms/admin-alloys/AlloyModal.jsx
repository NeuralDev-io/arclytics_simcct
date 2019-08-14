import React, { Component } from 'react'
import PropTypes from 'prop-types'
import XIcon from 'react-feather/dist/icons/x'
import { IconButton } from '../../elements/button'
import Modal from '../../elements/modal'
import TextField from '../../elements/textfield'
import PeriodicTable, { PeriodicTableData } from '../../elements/periodic-table'

import styles from './AlloyModal.module.scss'

class AlloyModal extends Component {
  constructor(props) {
    super(props)
    const { compositions = [] } = this.props
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
    const { elements } = this.state
    const { show, onClose } = this.props
    return (
      <Modal show={show} className={styles.modal}>
        <div className={styles.periodic}>
          <PeriodicTable elements={elements} onToggleElement={this.handleToggleElement} />
        </div>
        <div className={styles.content}>
          <IconButton
            onClick={onClose}
            Icon={props => <XIcon {...props} />}
            className={styles.closeButton}
          />
          <div className={styles.elementContainer}>
            {this.renderElements()}
          </div>
        </div>
      </Modal>
    )
  }
}

AlloyModal.propTypes = {
  compositions: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default AlloyModal
