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
import { Card, withStyles } from '@material-ui/core'
import clsx from 'clsx'

const defaultStyles = {
  root: {
    minHeight: '24rem',
    maxHeight: '35rem',
  },
}

function CardComponent(props) {
  const {
    classes, children, className, ...other
  } = props

  return (
    <Card className={clsx(classes.root, className)} {...other}>
      {children || ''}
    </Card>
  )
}

CardComponent.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node.isRequired,
  classes: PropTypes.node.isRequired,
}

CardComponent.defaultProps = {
  className: undefined,
}

export default withStyles(defaultStyles)(CardComponent)
