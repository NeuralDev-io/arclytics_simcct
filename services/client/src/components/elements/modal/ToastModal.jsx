import React from 'react'
import PropTypes from 'prop-types'
import XIcon from 'react-feather/dist/icons/x'
import { IconButton } from '../button'

import styles from './ToastModal.module.scss'

const ToastModal = ({
  show = false,
  withCloseIcon = false,
  onClose = () => {},
  className: { container = '', modal = '' },
  children,
}) => (
  <div className={`${styles.modalContainer} ${show ? styles.visible : ''} ${withCloseIcon && styles.withCloseIcon} ${container}`}>
    <div className={`${styles.modal} ${modal}`}>
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
  className: PropTypes.shape({
    container: PropTypes.string,
    modal: PropTypes.string,
  }),
  children: PropTypes.node,
}

ToastModal.defaultProps = {
  className: {
    container: '',
    modal: '',
  },
  children: null,
  withCloseIcon: false,
  onClose: () => {},
}

export default ToastModal
