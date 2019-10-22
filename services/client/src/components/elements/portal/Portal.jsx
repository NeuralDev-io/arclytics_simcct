/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Wrapper component to implement React Portal. This is a new feature
 * in React 16. This component takes a `to` prop and will render all
 * of its children into a newly-created div inside the `to` (which
 * should be a node).
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'

class Portal extends React.PureComponent {
  constructor(props) {
    super(props)
    this.el = document.createElement('div')
  }

  componentDidMount() {
    const { to } = this.props
    to.appendChild(this.el)
  }

  componentWillUnmount() {
    const { to } = this.props
    to.removeChild(this.el)
  }

  render() {
    const { children } = this.props
    return ReactDOM.createPortal(children, this.el)
  }
}

Portal.propTypes = {
  to: PropTypes.node.isRequired,
  children: PropTypes.elementType.isRequired,
}

export default Portal
