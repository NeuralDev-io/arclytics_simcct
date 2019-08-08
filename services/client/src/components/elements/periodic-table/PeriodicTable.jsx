import React, { Component } from 'react'
import data from './data'
import { buttonize } from '../../../utils/accessibility'

import styles from './PeriodicTable.module.scss'

class PeriodicTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      active: {},
      hovering: 0,
    }
  }

  handleToggleElement = (number) => {
    this.setState((prevState) => {
      const newActive = prevState.active
      if (newActive[number] !== undefined) {
        delete newActive[number]
      } else {
        newActive[number] = true
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
    } = elem
    const { active, hovering } = this.state
    let popupPos = ''
    if (xpos <= 9 && ypos <= 5) popupPos = 'popupTopRight'
    if (xpos > 9 && ypos <= 5) popupPos = 'popupTopLeft'
    if (xpos <= 9 && ypos > 5) popupPos = 'popupBottomRight'
    if (xpos > 9 && ypos > 5) popupPos = 'popupBottomLeft'

    return (
      <div
        key={number}
        className={`${styles.elementContainer} ${styles[`col${xpos}`]} ${styles[`row${ypos}`]}`}
        onMouseEnter={() => this.handleMouseEnter(number)}
        onMouseLeave={() => this.handleMouseLeave(number)}
        {...buttonize(() => this.handleToggleElement(number))}
      >
        <div className={`${styles.element} ${typeof active[number] !== 'undefined' && styles.active}`}>
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

export default PeriodicTable
