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
    const {
      children,
      position,
      overlap,
      className,
    } = this.props
    const { visible } = this.state

    return (
      <div className={`${styles.modalContainer} ${className}`} ref={(node) => { this.node = node }}>
        {React.Children.map(children, (child, i) => {
          if (i === 0) {
            return React.cloneElement(child, { onClick: this.handleClick })
          }
          return (
            <div className={`${styles.modal} ${visible && styles.visible} ${styles[`${position}${overlap ? 'Overlap' : ''}`]}`}>
              {child}
            </div>
          )
        })}
      </div>
    )
  }
}

AttachModal.propTypes = {
  // AttachModal accepts 2 children, the first being the interactive element
  // (usually a button), the second being the modal content
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired,
  // prop to set the position of the modal relative to interactive element
  // topLeft || topRight || bottomLeft || bottomRight
  position: PropTypes.string,
  // prop to set if modal is going to overlap interactive element
  overlap: PropTypes.bool,
  // className prop to override scss styles
  className: PropTypes.string,
}

AttachModal.defaultProps = {
  position: 'bottomLeft',
  overlap: true,
  className: '',
}

export default AttachModal
