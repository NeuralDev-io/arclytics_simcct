/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * This file contains several components which are wrapper around the
 * Route component of 'react-router-dom' to provide extra protection
 * using authorisation checking endpoint.
 *
 * @version 1.0.0
 * @author Dalton Le
 */

/**
* PrivateRoute only allows authenticated users to access
*/
// eslint-disable-next-line max-classes-per-file
import React from 'react'
import PropTypes from 'prop-types'
import { Route, Redirect } from 'react-router-dom'
import { checkAuthStatus } from '../../../api/AuthenticationHelper'

export class PrivateRoute extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: true,
      isAuthenticated: false,
      isAdmin: false,
    }
  }

  componentDidMount = () => {
    checkAuthStatus()
      .then((res) => {
        if (res.status === 'success') {
          this.setState({
            isLoading: false,
            isAuthenticated: true,
            isAdmin: res.admin,
          })
        }
        this.setState({ isLoading: false })
      })
  }

  render() {
    const { component: Component, ...rest } = this.props
    const { isAuthenticated, isLoading, isAdmin } = this.state
    if (isLoading) return <div />
    if (!isAuthenticated) return <Redirect to="/signin" />
    return (
      <Route
        {...rest}
        render={props => <Component {...props} isAdmin={isAdmin} isAuthenticated />}
      />
    )
  }
}

PrivateRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
}

/**
 * AdminRoute only allows users with admin privilege to access
 */
export class AdminRoute extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: true,
      isAuthenticated: false,
      isAdmin: true,
    }
  }

  componentDidMount = () => {
    checkAuthStatus()
      .then((res) => {
        if (res.status === 'success') {
          this.setState({
            isLoading: false,
            isAuthenticated: true,
            isAdmin: res.admin,
          })
        }
        this.setState({ isLoading: false })
      })
  }

  render() {
    const { component: Component, ...rest } = this.props
    const { isAuthenticated, isLoading, isAdmin } = this.state
    if (isLoading) return <div />
    if (!isAuthenticated) return <Redirect to="/signin" />
    if (!isAdmin) return <Redirect to="/" />
    return <Route {...rest} render={props => <Component {...props} isAdmin />} />
  }
}

AdminRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
}

/**
 * DemoRoute is a special route used for non-users.
 * Everyone can access DemoRoutes, but authenticated users will be
 * redirected to the root route at '/'
 */
export class DemoRoute extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: true,
      isAuthenticated: false,
    }
  }

  componentDidMount = () => {
    checkAuthStatus()
      .then((res) => {
        if (res.status === 'success') {
          this.setState({
            isLoading: false,
            isAuthenticated: true,
          })
        }
        this.setState({ isLoading: false })
      })
  }

  render() {
    const { component: Component, ...rest } = this.props
    const { isAuthenticated, isLoading } = this.state
    if (isLoading) return <div />
    if (isAuthenticated) return <Redirect to="/" />
    return (
      <Route
        {...rest}
        render={props => (
          <Component {...props} isAdmin={false} isAuthenticated={isAuthenticated} />
        )}
      />
    )
  }
}

DemoRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
}

/**
 * ShareRoute is a special route used for sharing links
 */
export class ShareRoute extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: true,
      isAuthenticated: false,
    }
  }

  componentDidMount = () => {
    checkAuthStatus()
      .then((res) => {
        if (res.status === 'success') {
          this.setState({
            isLoading: false,
            isAuthenticated: true,
          })
        }
        this.setState({ isLoading: false })
      })
  }

  render() {
    const { component: Component, ...rest } = this.props
    const { isAuthenticated, isLoading } = this.state
    if (isLoading) return <div />
    return (
      <Route
        {...rest}
        render={props => (
          <Component {...props} isAdmin={false} isAuthenticated={isAuthenticated} />
        )}
      />
    )
  }
}

ShareRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
}
