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
import { Card } from '@material-ui/core'
import clsx from 'clsx'

import styles from './Card.module.scss'

function CardComponent(props) {
  const { classes, children, className, ...other } = props

  return (
    <Card className={clsx(styles.root, className)} {...other}>
      <div className={clsx(styles.content, className)}>
        {children || ''}
      </div>
    </Card>
  )
}

CardComponent.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node
}

export default CardComponent
