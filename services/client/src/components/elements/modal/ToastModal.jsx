import React from 'react'
import PropTypes from 'prop-types'

import styles from './ToastModal.module.scss'

const ToastModal = ({
  show = false,
  className,
  children,
}) => (
  <div className={`${styles.modal} ${show ? styles.visible : ''} ${className}`}>
    {children}
  </div>
)

ToastModal.propTypes = {
  show: PropTypes.bool.isRequired,
  className: PropTypes.string,
  children: PropTypes.node,
}

ToastModal.defaultProps = {
  className: '',
  children: null,
}

export default ToastModal
