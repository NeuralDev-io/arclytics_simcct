/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Standard modal component.
 *
 * @version 1.2.0
 * @author Dalton Le, Arvy Salazar
 */
import React from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimes } from '@fortawesome/pro-light-svg-icons/faTimes'
import { IconButton } from '../button'
import Portal from '../portal'
import { buttonize } from '../../../utils/accessibility'

import styles from './Modal.module.scss'

const Modal = ({
  show = false,
  withCloseIcon = false,
  onClose = () => {},
  className,
  children,
}) => (
  <Portal to={document.getElementById('modal-container')}>
    <div className={`${styles.container} ${show ? styles.show : ''}`}>
      <div className={styles.backdrop} {...buttonize(onClose)} />
      <div className={`${styles.modalContainer} ${withCloseIcon && styles.withCloseIcon}`}>
        <div className={`${styles.modal} ${className || ''}`}>
          {children}
        </div>
        { withCloseIcon
        && (
          <IconButton
            onClick={onClose}
            Icon={props => <FontAwesomeIcon icon={faTimes} className={styles.icon} size="lg" {...props} />}
            className={{ button: styles.closeButton }}
          />
        )}
      </div>
    </div>
  </Portal>
)

Modal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func,
  className: PropTypes.string,
  children: PropTypes.node,
  withCloseIcon: PropTypes.bool,
}

Modal.defaultProps = {
  className: '',
  children: null,
  withCloseIcon: false,
  onClose: () => {},
}

export default Modal
