import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import styles from './Accordion.module.scss'

class Accordion extends PureComponent {
  render() {
    const { children } = this.props

    return (
      <div className={styles.container}>
        {children}
      </div>
    )
  }
}

Accordion.propTypes = {
  children: PropTypes.instanceOf(Object).isRequired,
}

export default Accordion
