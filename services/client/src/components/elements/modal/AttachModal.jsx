/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AttachModal component. The modal that pops up will attach to
 * the first child of the AttachModal component.
 *
 * @version 1.0.1
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './AttachModal.module.scss'

class AttachModal extends Component {
  handleClick = () => {
    const { visible, handleShow, handleClose } = this.props
    if (!visible) {
      // show modal
      handleShow()
      // attach event handler
      document.addEventListener('click', this.handleOutsideClick, false)
    } else {
      handleClose()
      // remove event handler
      document.removeEventListener('click', this.handleOutsideClick, false)
    }
  }

  handleOutsideClick = (e) => {
    // ignore clicks on the component itself
    if (this.node && this.node.contains(e.target)) {
      return
    }

    const { handleClose } = this.props
    handleClose()
  }

  render() {
    const {
      children,
      position,
      overlap,
      className,
      visible,
    } = this.props

    return (
      <div className={`${styles.modalContainer} ${className}`} ref={(node) => { this.node = node }}>
        {React.Children.map(children, (child, i) => {
          if (i === 0) {
            return React.cloneElement(child, {
              onClick: this.handleClick,
            })
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
  // props to control visibility, visible will be defined in state of parent component
  visible: PropTypes.bool.isRequired,
  handleShow: PropTypes.func.isRequired,
  handleClose: PropTypes.func.isRequired,
}

AttachModal.defaultProps = {
  position: 'bottomLeft',
  overlap: true,
  className: '',
}

export default AttachModal
