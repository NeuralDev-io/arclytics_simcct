import React, { Component } from 'react'
import ErrorBoundary from '../error-boundary'

class TestRoute extends Component {
  constructor(props) {
    super(props)
    this.state = {
      err: false,
    }
  }

  // error = () => {
  //   throw new Error('Test crashed!')
  // }

  render() {
    const { err } = this.state
    if (err) {
      throw new Error('Test error!')
    }
    return (
      <div>
        This is a test route.
          <button type="button" onClick={() => this.setState({ err: true })}>
            Click to crash app
          </button>
      </div>
    )
  }
}

export default TestRoute
