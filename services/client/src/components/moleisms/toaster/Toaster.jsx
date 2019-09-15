import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withSnackbar } from 'notistack'
import Button from '../../elements/button'
import { removeFlashToast } from '../../../state/ducks/toast/actions'

class Toaster extends React.Component {
  state = {
    displayed: [],
  }

  storeDisplayed = (key) => {
    this.setState(({ displayed }) => ({
      displayed: [...displayed, key],
    }))
  }

  render() {
    const {
      notifications,
      enqueueSnackbar,
      closeSnackbar,
      removeFlashToastConnect,
    } = this.props
    const { displayed } = this.state

    notifications.forEach((notification) => {
      setTimeout(() => {
        // If notification already displayed, abort
        if (displayed.indexOf(notification.key) > -1) return
        // Display notification using notistack
        if (notification.dismissable) {
          enqueueSnackbar(notification.message, {
            ...notification.options,
            action: key => (
              <Button
                appearance="text"
                className="snackbar__button"
                onClick={() => closeSnackbar(key)}
              >
                Dismiss
              </Button>
            ),
          })
        } else enqueueSnackbar(notification.message, notification.options)
        // Add notification's key to the local state
        this.storeDisplayed(notification.key)
        // Dispatch action to remove the notification from the redux store
        removeFlashToastConnect(notification.key)
      }, 1)
    })

    return null
  }
}

Toaster.propTypes = {
  enqueueSnackbar: PropTypes.func.isRequired,
  closeSnackbar: PropTypes.func.isRequired,
  // from connect
  removeFlashToastConnect: PropTypes.func.isRequired,
  notifications: PropTypes.arrayOf(PropTypes.number).isRequired,
}

const mapStateToProps = state => ({
  notifications: state.toast.notifications,
})

const mapDispatchToProps = {
  removeFlashToastConnect: removeFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(withSnackbar(Toaster))
