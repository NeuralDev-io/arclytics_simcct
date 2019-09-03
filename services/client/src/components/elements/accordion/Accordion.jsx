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
    const { children } = this.props
    if (expand.length === 0) {
      this.setState({ expand: new Array(children.length).fill(false) })
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
}

export default Accordion
