/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Error Boundary
 *
 * @version 1.0.0
 * @author Arvy Salazar, Andrew Che, Dalton Le
 *
 * This component is a default catch all for 404 errors within the application.
 * Additionally, for every error caught, we will send an API request to the
 * EFK stack logging service in the backend to register the error.
 *
 */

import React from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import { ReactComponent as WarningImage } from '../../../assets/undraw_react_y7wq.svg'
import styles from './ErrorBoundary.module.scss'
import { logError } from '../../../api/LoggingHelper'

/*
  If you are wondering why react still shows the react error in production
  https://stackoverflow.com/questions/52096804/react-still-showing-errors-after-catching-with-errorboundary.
*/

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { error }
  }

  componentDidCatch(error, errorInfo) {
    // Catch errors in any components below and re-render with error message
    this.setState({
      error,
      errorInfo,
    })
    logError(error.toString(), error.message, 'ErrorBoundary', error.stack)
  }

  handleRefreshPage = () => {
    window.location.reload()
  }

  render() {
    const { error, errorInfo } = this.state
    const { children } = this.props
    if (errorInfo || error) {
      // Error path
      return (
        <div>
          <div className={styles.container}>
            <WarningImage className={styles.warningImage} />
            <h2>Oops something went wrong</h2>
            <span>
              We might have lost a few electrons. We are hard at work trying to find it.
              <br />
              Meanwhile, try reloading the page or check your connection.
            </span>
            <Button className={styles.refreshButton} onClick={this.handleRefreshPage} length="long">Refresh page</Button>
          </div>
        </div>
      )
    }
    // Normally, just render children
    return children
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ErrorBoundary
