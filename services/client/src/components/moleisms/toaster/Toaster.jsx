/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Redux implementation of the snackbar from 'notistack'.
 * This Toaster component watches for any notification that is added to
 * the Redux store and create a Snackbar using the 'notistack' package,
 * then remove this notification from the Redux store.
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withSnackbar } from 'notistack'
import Button from '../../elements/button'
import { removeFlashToast } from '../../../state/ducks/toast/actions'

class Toaster extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      displayed: [],
    }
  }

  handleStoreDisplayed = (key) => {
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
        if (displayed.includes(notification.key)) return
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
        this.handleStoreDisplayed(notification.key)
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
  notifications: PropTypes.arrayOf(PropTypes.shape({
    message: PropTypes.string,
    options: PropTypes.shape({}),
    key: PropTypes.number,
    dismissable: PropTypes.bool,
  })).isRequired,
}

const mapStateToProps = state => ({
  notifications: state.toast.notifications,
})

const mapDispatchToProps = {
  removeFlashToastConnect: removeFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(withSnackbar(Toaster))
