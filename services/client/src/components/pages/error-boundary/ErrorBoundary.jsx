import React from 'react'
import PropTypes from 'prop-types'
import { ReactComponent as WarningImage } from '../../../assets/undraw_warning_cyit.svg'

/*
  If you are wondering why react still shows the react error
  https://stackoverflow.com/questions/52096804/react-still-showing-errors-after-catching-with-errorboundary.
*/

// TODO: add an error screen and add logging function
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
    // Log error messages to logger here
  }

  render() {
    const { error, errorInfo } = this.state
    const { children } = this.props
    if (errorInfo) {
      // Error path
      return (
        <div>
          <h2>Something went wrong.</h2>
            <WarningImage className={styles.warningImage} />
            {error && error.toString()}
            <br />
            {errorInfo.componentStack}
          </details>
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
