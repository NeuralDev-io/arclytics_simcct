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
    return <Route {...rest} render={props => <Component {...props} isAdmin={isAdmin} />} />
  }
}

PrivateRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
}

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
    return <Route {...rest} render={props => <Component {...props} isAdmin={isAdmin} />} />
  }
}

AdminRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
}
