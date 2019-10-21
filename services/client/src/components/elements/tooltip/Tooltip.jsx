/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Tooltip component. To use this component, pass 2 children to it.
 * The first child will become the interactive element, the second
 * child will be the content of the tooltip.
 *
 * @version 1.0.0
 * @author Dalton Le
 */


import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './Tooltip.module.scss'

class Tooltip extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
    }
  }

  handleMouseEnter = () => this.setState({ visible: true })

  handleMouseLeave = () => this.setState({ visible: false })

  render() {
    const {
      children,
      position,
      className: {
        container = '',
        tooltip = '',
      },
    } = this.props
    const { visible } = this.state

    return (
      <div className={`${styles.container} ${container}`}>
        {React.Children.map(children, (child, i) => {
          if (i === 0) {
            return React.cloneElement(child, {
              onMouseEnter: this.handleMouseEnter,
              onMouseLeave: this.handleMouseLeave,
            })
          }
          return (
            <div className={`${styles.tooltip} ${visible && styles.visible} ${styles[position]} ${tooltip}`}>
              {child}
            </div>
          )
        })}
      </div>
    )
  }
}

Tooltip.propTypes = {
  // AttachModal accepts 2 children, the first being the interactive element
  // (usually a button), the second being the modal content
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired,
  // prop to set the position of the modal relative to interactive element
  // top || right || bottom || left
  position: PropTypes.string,
  // className prop to override scss styles
  className: PropTypes.shape({
    container: PropTypes.string,
    tooltip: PropTypes.string,
  }),
}

Tooltip.defaultProps = {
  position: 'bottom',
  className: {
    container: '',
    tooltip: '',
  },
}

export default Tooltip
