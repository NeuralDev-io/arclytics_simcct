import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import { connect } from 'react-redux'

import { getUserProfile } from '../../../state/ducks/self/actions'

import AppBar from '../../moleisms/appbar'
import UserSidebar from '../../moleisms/user-sidebar'
import ProfilePage from '../../moleisms/user-profile'
import UserAlloys from '../../moleisms/user-alloys'
import UserSavedSimulations from '../../moleisms/user-sim'

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
      <React.Fragment>
        <AppBar active="user" redirect={history.push} isAdmin={isAdmin} />
        <div className={styles.sidebar}>
          {/* A sidebar with the sub navigation for the children components. */}
          <UserSidebar />
        </div>
        <div className={styles.main}>
          {/* Define the routes for the right panel. */}
          <Route path="/user/profile" render={props => <ProfilePage {...props} userProf={user} />} />
        </div>
      </React.Fragment>
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
