import React from 'react'
import PropTypes from 'prop-types'
import XIcon from 'react-feather/dist/icons/x'
import { IconButton } from '../button'

import styles from './ToastModal.module.scss'

const ToastModal = ({
  show = false,
  withCloseIcon = false,
  onClose = () => {},
  className,
  children,
}) => (
  <div className={`${styles.modalContainer} ${show ? styles.visible : ''} ${withCloseIcon && styles.withCloseIcon}`}>
    <div className={`${styles.modal} ${className}`}>
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
)

ToastModal.propTypes = {
  show: PropTypes.bool.isRequired,
  withCloseIcon: PropTypes.bool,
  onClose: PropTypes.func,
  className: PropTypes.string,
  children: PropTypes.node,
}

ToastModal.defaultProps = {
  className: '',
  children: null,
  withCloseIcon: false,
  onClose: () => {},
}

export default ToastModal
