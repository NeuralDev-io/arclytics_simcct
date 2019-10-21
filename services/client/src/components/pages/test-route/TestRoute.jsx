/*
* This source code is licensed under the MIT license found in the
* LICENSE file in the root directory of this repository.
*
* App Component
*
* @version 1.2.0
* @author Dalton Le, Arvy Salazar, Andrew Che
*
* DECISION:
* This was only use for testing of the ErrorBoundary and Logs so we will keep it here
* in case we may need to test some other errors in the future.
*
* */

import React, { Component } from 'react'

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

// noinspection JSUnusedGlobalSymbols
export default TestRoute
