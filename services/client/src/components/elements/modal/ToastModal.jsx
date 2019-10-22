/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * ToastModal component. The modal that pops up from the bottom of the
 * screen, often used for a banner/announcement.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'
import XIcon from 'react-feather/dist/icons/x'
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
// import {faTimes } from '@fortawesome/pro-light-svg-icons/faTimes'
import { IconButton } from '../button'
// <FontAwesomeIcon icon={faTimes} className={styles.icon} size="lg" />


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
        className={{ button: styles.closeButton }}
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
