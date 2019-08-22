import React from 'react'
import PropTypes from 'prop-types'
import XIcon from 'react-feather/dist/icons/x'
import { IconButton } from '../button'
import { buttonize } from '../../../utils/accessibility'

import styles from './Modal.module.scss'

const Modal = ({
  show = false,
  withCloseIcon = false,
  onClose = () => {},
  className,
  children,
  clicked,
}) => (
  <div className={`${styles.container} ${show ? styles.show : ''}`}>
    <div className={styles.backdrop} {...buttonize(clicked)} />
    <div className={`${styles.modalContainer} ${withCloseIcon && styles.withCloseIcon}`}>
      <div className={`${styles.modal} ${className || ''}`}>
        {children}
      </div>
      { withCloseIcon
      && (
        <IconButton
          onClick={onClose}
          Icon={props => <XIcon {...props} />}
          className={styles.closeButton}
        />
      )}
    </div>
  </div>
)

Modal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func,
  className: PropTypes.string,
  children: PropTypes.node,
  clicked: PropTypes.func,
  withCloseIcon: PropTypes.bool,
}

Modal.defaultProps = {
  className: '',
  children: null,
  clicked: null,
  withCloseIcon: false,
  onClose: () => {},
}

export default Modal
