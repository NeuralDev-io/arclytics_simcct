/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Redux implementation to help navigate outside of the component tree.
 * This Redirector component watches for the redirector in Redux state
 * and navigates to the location that gets added to the redirector state.
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { removeLocation } from '../../../state/ducks/redirector/actions'

class Redirector extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      navigated: [],
    }
  }

  handleNavigateLocation = (key) => {
    this.setState(({ navigated }) => ({
      navigated: [...navigated, key],
    }))
  }

  render() {
    const {
      locations,
      removeLocationConnect,
      history,
      location: { pathname },
    } = this.props
    const { navigated } = this.state

    locations.forEach((loc) => {
      // if already navigated to this location, abort
      if (loc.location.pathname === pathname || navigated.includes(loc.key)) return
      // Dispatch action to remove the location from the redux store
      removeLocationConnect(loc.key)
      // navigate to this new location
      history.push(loc.location)
    })

    return null
  }
}

Redirector.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string,
  }).isRequired,
  // from connect
  removeLocationConnect: PropTypes.func.isRequired,
  locations: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.number,
    location: PropTypes.arrayOf(PropTypes.shape({
      pathname: PropTypes.string,
      state: PropTypes.shape({}),
      search: PropTypes.string,
    })),
  })).isRequired,
}

const mapStateToProps = state => ({
  locations: state.redirector.locations,
})

const mapDispatchToProps = {
  removeLocationConnect: removeLocation,
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Redirector))
