/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * SignupModal: A ToastModal that pops up in the demo version to asks user
 * to sign up for the app.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { ToastModal } from '../../elements/modal'
import Button from '../../elements/button'

import styles from './SignupModal.module.scss'

export class SignupModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      show: false,
    }
  }

  componentDidMount = () => {
    const { show = false } = this.props
    if (show) {
      this.timer = setTimeout(() => this.setState({ show: true }), 3000)
    }
  }

  componentWillUnmount = () => {
    if (this.timer) {
      clearTimeout(this.timer)
      this.timer = 0
    }
  }

  render() {
    const { show } = this.state
    const { redirect } = this.props
    return (
      <ToastModal show={show}>
        <div className={styles.modal}>
          <h6>Sign up to enjoy the full Arclytics SimCCT experience.</h6>
          <Button
            onClick={() => redirect('/signup')}
          >
            SIGN UP
          </Button>
          <Button
            onClick={() => redirect('/signin')}
            appearance="text"
          >
            SIGN IN
          </Button>
        </div>
      </ToastModal>
    )
  }
}

SignupModal.propTypes = {
  show: PropTypes.bool.isRequired,
  redirect: PropTypes.func.isRequired,
}

export default (SignupModal)
