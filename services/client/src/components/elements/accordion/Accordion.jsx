/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Accordion component, to be used with the AccordionSection component.
 *
 * @version 1.0.0
 * @author Andrew Che, Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './Accordion.module.scss'

class Accordion extends Component {
  constructor(props) {
    super(props)
    this.state = {
      expand: [],
    }
  }

  componentDidMount = () => {
    const { expand } = this.state
    const { children, defaultExpand } = this.props
    if (expand.length === 0) {
      const newExpand = new Array(children.length).fill(false)
      if (defaultExpand !== -1) newExpand[defaultExpand] = true
      this.setState({ expand: newExpand })
    }
  }

  handleToggle = (index) => {
    this.setState((state) => {
      const newExpand = state.expand
      newExpand[index] = !state.expand[index]
      return { expand: newExpand }
    })
  }

  render() {
    const { children } = this.props
    const { expand } = this.state

    return (
      <div className={styles.container}>
        {React.Children.map(children, (child, i) => (
          React.cloneElement(child, {
            onToggle: () => this.handleToggle(i),
            expanded: expand[i],
          })
        ))}
      </div>
    )
  }
}

Accordion.propTypes = {
  children: PropTypes.instanceOf(Object).isRequired,
  defaultExpand: PropTypes.number,
}

Accordion.defaultProps = {
  defaultExpand: -1,
}

export default Accordion
