/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User page rendered by '/user'
 *
 * @version 1.0.0
 * @author Dalton Le, Andrew Che
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import { connect } from 'react-redux'

import { getUserProfile } from '../../../state/ducks/self/actions'

import AppBar from '../../moleisms/appbar'
import UserSidebar from '../../moleisms/user-sidebar'
import ProfilePage from '../../moleisms/user-profile'

import styles from './UserPage.module.scss'

class UserPage extends Component {
  /**
   * User page is a parent component that adds the `components/moleisms/UserSidebar
   * and a right panel with pages for user profile, alloys database, and saved
   * simulations.
   */

  componentDidMount() {
    getUserProfile()
  }

  render() {
    // this.props.getUserProfileConnect()
    const { history, user, isAdmin } = this.props
    return (
      <>
        <AppBar active="user" redirect={history.push} isAdmin={isAdmin} isAuthenticated />
        <div className={styles.sidebar}>
          {/* A sidebar with the sub navigation for the children components. */}
          <UserSidebar />
        </div>
        <div className={styles.main}>
          {/* Define the routes for the right panel. */}
          <Route path="/user/profile" render={props => <ProfilePage {...props} userProf={user} />} />
        </div>
      </>
    )
  }
}

UserPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
}

const mapStateToProps = state => ({
  user: state.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
}

export default connect(mapStateToProps, mapDispatchToProps)(UserPage)
