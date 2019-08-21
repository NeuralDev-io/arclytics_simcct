import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './AttachModal.module.scss'

class AttachModal extends Component {
  constructor() {
    super()
    this.state = {
      visible: false,
    }
  }

  handleClick = () => {
    const { visible } = this.state
    if (!visible) {
      // attach/remove event handler
      document.addEventListener('click', this.handleOutsideClick, false)
    } else {
      document.removeEventListener('click', this.handleOutsideClick, false)
    }

    this.setState(prevState => ({
      visible: !prevState.visible,
    }))
  }

  handleOutsideClick = (e) => {
    // ignore clicks on the component itself
    if (this.node.contains(e.target)) {
      return
    }

    this.handleClick()
  }

  render() {
    const { children, position, overlap } = this.props
    const { visible } = this.state
    console.log(`${position}${overlap && 'Overlap'}`)
    return (
      <div className={styles.modalContainer} ref={(node) => { this.node = node }}>
        {React.Children.map(children, (child, i) => {
          if (i === 0) {
            return React.cloneElement(child, { onClick: this.handleClick })
          }
          return (
            visible
            && <div className={`${styles.modal} ${styles[`${position}${overlap ? 'Overlap' : ''}`]}`}>{child}</div>
          )
        })}
      </div>
    )
  }
}

AttachModal.propTypes = {
  // prop to set the position of the modal relative to interactive element
  // topLeft || topRight || bottomLeft || bottomRight
  position: PropTypes.string,
  // prop to set if modal is going to overlap interactive element
  overlap: PropTypes.bool,
}

AttachModal.defaultProps = {
  position: 'bottomLeft',
  overlap: true,
}

export default AttachModal
