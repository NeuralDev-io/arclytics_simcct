import React  from 'react'
import PropTypes from 'prop-types'

import styles from './Modal.module.scss'

const Modal = (props) =>{
    const {
        show = false,
        className,
        children,
        clicked
    } = props
    
    const classname = `${className || ''} ${styles.default} ${show ? styles.show: ''} `

    return(
        <div>
            {/* TODO: (arvy@neuraldev.io) Since there are tutorials later on might want to change the backdrop as another component */}
            {show ? (<div className={styles.Backdrop} onClick={clicked}></div>) : ('')}
            <div className={classname} show={show}>
                {children}
            </div>
        </div>
    )
}

Modal.propTypes = {
    show: PropTypes.bool,
    className: PropTypes.string,
    children: PropTypes.node,
    clicked: PropTypes.func
}

Modal.defaultProps = {
    show: false,
}
  
export default Modal; 