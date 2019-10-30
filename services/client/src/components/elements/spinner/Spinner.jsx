/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Spinner components. Include it anywhere to render it.
 * Inline spinner will be used in-line, typically inside a loading
 * component.
 * PageSpinner is coming soon, supposed to load a spinner which suspense
 * all activities of the application.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import PropTypes from 'prop-types'

import styles from './Spinner.module.scss'

const InlineSpinner = ({ size }) => (
  <div className={`${styles.inline} animate-inf-rotate-cc ${size === 'lg' ? styles.lg : ''}`} />
)

InlineSpinner.propTypes = {
  size: PropTypes.string,
}

InlineSpinner.defaultProps = {
  size: 'default',
}

export default InlineSpinner
