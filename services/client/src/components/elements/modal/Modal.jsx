import React  from 'react'
import PropTypes from 'prop-types'

import styles from './Modal.module.scss'

const Modal = (props) =>{
    const {
        show = false,
        className,
        children
    } = props
    
    const classname = `${styles.default} ${show ? styles.show: ''} --text-btn ${className || ''}`

    return(
        <div className={styles.Backdrop}>
            <div className={classname} show={show}>
                {children}
            </div>
        </div>
    )
}

Modal.propTypes = {
    show: PropTypes.node.isRequired,
    children: PropTypes.node.isRequired
}
  
export default Modal; 