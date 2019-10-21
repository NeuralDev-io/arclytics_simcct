/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * SharePage: requests for a shared simulation using the token in the URL
 * and redirects to SimPage with the simulation loaded.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { loadSimFromLink } from '../../../state/ducks/sim/actions'

class SharePage extends Component {
  componentDidMount = () => {
    const { match, loadSimFromLinkConnect, history } = this.props
    loadSimFromLinkConnect(match.params.token)
      .then(() => {
        const { isAuthenticated } = this.props
        if (isAuthenticated) {
          history.push({
            pathname: '/',
            state: { loadFromShare: true },
          })
        } else {
          history.push('/demo')
        }
      })
  }

  render() {
    return (
      <div>
        Please wait while we&apos;re getting your data...
      </div>
    )
  }
}

SharePage.propTypes = {
  loadSimFromLinkConnect: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string,
    }),
  }).isRequired,
  history: PropTypes.shape({
    push: PropTypes.func,
  }).isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
}

const mapDispatchToProps = {
  loadSimFromLinkConnect: loadSimFromLink,
}

export default connect(null, mapDispatchToProps)(SharePage)
