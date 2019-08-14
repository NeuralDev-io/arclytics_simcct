import React, { Component } from 'react'
import data from './data'
import { buttonize } from '../../../utils/accessibility'

import styles from './PeriodicTable.module.scss'

class UncontrolledPeriodicTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      active: [],
      hovering: 0,
    }
  }

  handleToggleElement = (number) => {
    this.setState(({ active }) => {
      let newActive = active
      if (active.includes(number)) {
        newActive = active.filter(n => n !== number)
      } else {
        newActive.push(number)
      }
      return { active: newActive }
    })
  }

  handleMouseEnter = number => this.setState({ hovering: number })

  handleMouseLeave = () => this.setState({ hovering: 0 })

  renderElements = () => data.map((elem) => {
    const {
      number,
      xpos,
      ypos,
      symbol,
      name,
      atomic_mass, // eslint-disable-line
      category,
    } = elem
    const { active, hovering } = this.state
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
        <div className={`${styles.element} ${styles[colour()]} ${active.includes(number) && styles.active}`}>
          <span className={styles.number}>{number}</span>
          <span className={styles.symbol}>{symbol}</span>
        </div>
        <div
          className={`${styles[popupPos]} animate-fadein`}
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

export default UncontrolledPeriodicTable
