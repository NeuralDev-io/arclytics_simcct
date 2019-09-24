import React from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import { ReactComponent as WarningImage } from '../../../assets/undraw_warning_cyit.svg'
import styles from './ErrorBoundary.module.scss'

/*
  If you are wondering why react still shows the react error in production
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

  handleRefereshPage = () => {
    window.location.reload()
  }

  render() {
    const { error, errorInfo } = this.state
    const { children } = this.props
    if (errorInfo) {
      // Error path
      return (
        <div>
          <div className={styles.container}>
            <WarningImage className={styles.warningImage} />
            <h2>Oops!! something went wrong</h2>
            <span>
              Wait till we get the error fixed or you can
              try reloading the page or contacting us.
            </span>
            <Button className={styles.refreshButton} onClick={ this.handleRefereshPage } length="long">Refresh page</Button>
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
