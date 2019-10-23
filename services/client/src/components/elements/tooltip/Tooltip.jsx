/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Tooltip component. To use this component, pass 2 children to it.
 * The first child will become the interactive element, the second
 * child will be the content of the tooltip.
 *
 * @version 1.1.0
 * @author Dalton Le
 */


import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Portal from '../portal'

import styles from './Tooltip.module.scss'

class Tooltip extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
      style: {},
    }
    this.width = props.width || 'max-content'
    this.space = props.space || 16
  }

  // calculate position of the tooltip after it renders
  componentDidMount = () => {
    const { position } = this.props
    // this style object will be passed as the tooltip's 'style' prop
    const style = { width: this.width }
    // where on the screen is the target
    const dimensions = this.el.getBoundingClientRect()

    // position the tooltip based on whether we should display it horizontally
    // or vertically
    if (position === 'vertical') {
      // center align the tooltip by taking both the target and tooltip widths into account
      style.left = dimensions.left + dimensions.width / 2 - this.width / 2
      // make sure it doesn't poke off the left side of the page
      style.left = Math.max(this.space, style.left)
      style.left = Math.min(
        style.left,
        document.body.clientWidth - this.width - this.space,
      ) // or off the right

      if (dimensions.top < window.innerHeight / 2) {
        // the top half of the page
        // when on the top half of the page, position the top of the tooltip
        // just below the target (it will stretch downwards)
        style.top = dimensions.top + dimensions.height + this.space
      } else {
        // when on the bottom half, set the bottom of the tooltip
        // just above the top of the target (it will stretch upwards)
        style.bottom = window.innerHeight - dimensions.top + this.space
      }
    }
    if (position === 'horizontal') {
      // center align the tooltip by taking both the target and tooltip heights into account
      style.top = dimensions.top + dimensions.height / 2 - this.tooltipEl.clientHeight / 2
      // make sure it doesn't poke off the top side of the page
      style.top = Math.max(this.space, style.top)
      style.top = Math.min(
        style.top,
        window.innerHeight - this.tooltipEl.clientHeight - this.space,
      ) // or off the bottom

      if (dimensions.left < window.innerWidth / 2) {
        // the top half of the page
        style.left = dimensions.left + dimensions.width + this.space
      } else {
        style.right = window.innerWidth - dimensions.left + this.space
      }
    }

    window.onscroll = this.hideTooltip

    this.setState({
      style,
    })
  }

  showTooltip = () => {
    const { position } = this.props
    // this style object will be passed as the tooltip's 'style' prop
    const style = { width: this.width }
    // where on the screen is the target
    const dimensions = this.el.getBoundingClientRect()

    // position the tooltip based on whether we should display it horizontally
    // or vertically
    if (position === 'vertical') {
      // center align the tooltip by taking both the target and tooltip widths into account
      style.left = dimensions.left + dimensions.width / 2 - this.width / 2
      // make sure it doesn't poke off the left side of the page
      style.left = Math.max(this.space, style.left)
      style.left = Math.min(
        style.left,
        document.body.clientWidth - this.width - this.space,
      ) // or off the right

      if (dimensions.top < window.innerHeight / 2) {
        // the top half of the page
        // when on the top half of the page, position the top of the tooltip
        // just below the target (it will stretch downwards)
        style.top = dimensions.top + dimensions.height + this.space
      } else {
        // when on the bottom half, set the bottom of the tooltip
        // just above the top of the target (it will stretch upwards)
        style.bottom = window.innerHeight - dimensions.top + this.space
      }
    }
    if (position === 'horizontal') {
      // center align the tooltip by taking both the target and tooltip widths into account
      style.top = dimensions.top + dimensions.height / 2 - this.height / 2
      // make sure it doesn't poke off the left side of the page
      style.top = Math.max(this.space, style.top)
      style.top = Math.min(
        style.top,
        document.body.clientHeight - this.height - this.space,
      ) // or off the right

      if (dimensions.left < window.innerWidth / 2) {
        // the top half of the page
        // when on the top half of the page, position the top of the tooltip
        // just below the target (it will stretch downwards)
        style.left = dimensions.left + dimensions.width + this.space
      } else {
        // when on the bottom half, set the bottom of the tooltip
        // just above the top of the target (it will stretch upwards)
        style.right = window.innerWidth - dimensions.left + this.space
      }
    }

    // window.addEventListener('scroll', this.hideTooltip)

    this.setState({
      visible: true,
      style,
    })
  }

  hideTooltip = () => {
    // window.removeEventListener('scroll', this.hideTooltip)
    this.setState({ visible: false })
  }

  render() {
    const {
      children,
      className: {
        container = '',
        tooltip = '',
      },
    } = this.props
    const { visible, style } = this.state

    return (
      <div
        onMouseEnter={this.showTooltip}
        onMouseLeave={this.hideTooltip}
        className={container}
        ref={el => { this.el = el }}
      >
        {React.Children.map(children, (child, i) => {
          if (i === 0) {
            return child
          }
          return (
            <Portal to={document.getElementById('tooltip-container')}>
              <div
                className={`${styles.tooltip} ${visible && styles.visible} ${tooltip}`}
                style={style}
                ref={el => { this.tooltipEl = el }}
              >
                {child}
              </div>
            </Portal>
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
  // horizontal | vertical
  position: PropTypes.string,
  // className prop to override scss styles
  className: PropTypes.shape({
    container: PropTypes.string,
    tooltip: PropTypes.string,
  }),
  width: PropTypes.oneOfType([
    PropTypes.number, PropTypes.string,
  ]),
  space: PropTypes.number,
}

Tooltip.defaultProps = {
  position: 'horizontal',
  className: {
    container: '',
    tooltip: '',
  },
  width: 'max-content',
  space: 8,
}

export default Tooltip
