/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User sidebar.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import UserIcon from 'react-feather/dist/icons/user'
import DatabaseIcon from 'react-feather/dist/icons/database'
import SlidersIcon from 'react-feather/dist/icons/sliders'
import FeedbackIcon from 'react-feather/dist/icons/heart'
import Button from '../../elements/button'
import { updateFeedback } from '../../../state/ducks/feedback/actions'

import styles from './UserSidebar.module.scss'

class UserSidebar extends Component {
  constructor(props) {
    super(props)
    // We get the URL from the current window object and split on '/'
    const pathArr = window.location.pathname.split('/')

    this.state = {
      // Get the last element which is basically the same ID name in the below defined
      // navigation links to set the className style on it to make it `active`
      active: pathArr[pathArr.length - 1],
    }
  }

  handleOpenFeedback = () => {
    const { updateFeedbackConnect } = this.props
    updateFeedbackConnect({
      feedbackVisible: true,
      backdrop: true,
      givingFeedback: true,
    })
  }

  render() {
    const { active } = this.state
    return (
      <div className={styles.sidebar}>
        <h4>Account</h4>
        <Link
          id="profile"
          to="/user/profile"
          onClick={() => this.setState({ active: 'profile' })}
          className={`${styles.item} ${active === 'profile' && styles.active}`}
        >
          <UserIcon className={styles.icon} />
          <span>Profile</span>
        </Link>
        <Link
          id="alloy"
          to="/user/profile"
          onClick={() => this.setState({ active: 'profile' })}
          className={`${styles.item} ${active === 'alloys' && styles.active}`}
        >
          <DatabaseIcon className={styles.icon} />
          <span>Security</span>
        </Link>
        <Link
          id="simulations"
          to="/user/profile"
          onClick={() => this.setState({ active: 'profile' })}
          className={`${styles.item} ${active === 'simulations' && styles.active}`}
        >
          <SlidersIcon className={styles.icon} />
          <span>Data personalisation</span>
        </Link>
        <Button
          appearance="text"
          length="long"
          IconComponent={props => <FeedbackIcon {...props} />}
          className={styles.feedbackButton}
          onClick={this.handleOpenFeedback}
        >
          Give feedback
        </Button>
      </div>
    )
  }
}

UserSidebar.propTypes = {
  updateFeedbackConnect: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  updateFeedbackConnect: updateFeedback,
}

export default connect(null, mapDispatchToProps)(UserSidebar)
