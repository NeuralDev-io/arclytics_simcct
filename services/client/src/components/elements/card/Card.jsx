/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Card component
 *
 * A Material UI inspired wrapper around `@material-ui/core` card component.
 *
 * @version 0.0.1
 * @author Andrew Che
 */
import React from 'react'
import PropTypes from 'prop-types'

import styles from './Card.module.scss'

function CardComponent(props) {
  const {
    children, className, ...other
  } = props

  return (
    <div className={`${styles.card} ${className}`} {...other}>
      {children || ''}
    </div>
  )
}

CardComponent.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node.isRequired,
}

CardComponent.defaultProps = {
  className: undefined,
}

export default CardComponent
