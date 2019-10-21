/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Periodic table component, quite tightly coupled with AlloyModal
 * components in '/moleisms/admin-alloys/AlloyModal.jsx' or
 * '/moleisms/user-alloys/AlloyModal.jsx'
 *
 * @version 1.0.1
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { PERIODIC_TABLE_DATA } from '../../../utils/alloys'
import { buttonize } from '../../../utils/accessibility'

import styles from './PeriodicTable.module.scss'

class PeriodicTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hovering: 0,
    }
  }

  handleToggleElement = (number) => {
    const { elements, onToggleElement } = this.props
    let newElements = [...elements]
    if (elements.includes(number)) {
      newElements = newElements.filter(n => n !== number)
    } else {
      newElements.push(number)
    }
    onToggleElement(number, newElements)
  }

  handleMouseEnter = number => this.setState({ hovering: number })

  handleMouseLeave = () => this.setState({ hovering: 0 })

  renderElements = () => PERIODIC_TABLE_DATA.map((elem) => {
    const {
      number,
      xpos,
      ypos,
      symbol,
      name,
      atomic_mass, // eslint-disable-line
      category,
    } = elem
    const { hovering } = this.state
    const { elements = [] } = this.props
    let popupPos = ''
    if (xpos <= 9 && ypos <= 5) popupPos = 'popupTopRight'
    if (xpos > 9 && ypos <= 5) popupPos = 'popupTopLeft'
    if (xpos <= 9 && ypos > 5) popupPos = 'popupBottomRight'
    if (xpos > 9 && ypos > 5) popupPos = 'popupBottomLeft'
    const colour = () => {
      switch (category) {
        case 'transition metal': return 'r'
        case 'post-transition metal': return 'o'
        case 'alkali metal': return 'l'
        case 'alkaline earth metal': return 'g'
        case 'lanthanide': return 't'
        case 'actinide': return 'b'
        case 'metalloid': return 'i' // or semimetals
        case 'noble gas': return 'v'
        case 'diatomic nonmetal': return 'm'
        case 'polyatomic nonmetal': return 'm'
        default: return 'br'
      }
    }

    return (
      <div
        key={number}
        className={`${styles.elementContainer} ${styles[`col${xpos}`]} ${styles[`row${ypos}`]}`}
        onMouseEnter={() => this.handleMouseEnter(number)}
        onMouseLeave={() => this.handleMouseLeave(number)}
        {...buttonize(() => this.handleToggleElement(number))}
      >
        <div className={`${styles.element} ${styles[colour()]} ${elements.includes(number) && styles.active}`}>
          <span className={styles.number}>{number}</span>
          <span className={styles.symbol}>{symbol}</span>
        </div>
        <div
          className={`${styles[popupPos]}`}
          style={{ display: hovering === number ? 'block' : 'none' }}
        >
          <div className={styles.elementDetail}>
            <span className={styles.number}>{number}</span>
            <span className={styles.symbol}>{symbol}</span>
            <span className={styles.name}>{name}</span>
            <span className={styles.mass}>[{atomic_mass}]</span> {/* eslint-disable-line */}
          </div>
          <p>{elem.summary}</p>
        </div>
      </div>
    )
  })

  render() {
    return (
      <div className={styles.container}>
        {this.renderElements()}
      </div>
    )
  }
}

PeriodicTable.propTypes = {
  elements: PropTypes.arrayOf(PropTypes.number),
  onToggleElement: PropTypes.func.isRequired,
}

PeriodicTable.defaultProps = {
  elements: [],
}

export default PeriodicTable
