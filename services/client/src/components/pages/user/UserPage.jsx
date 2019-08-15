import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import { connect } from 'react-redux'

import AppBar from '../../moleisms/appbar'
import UserSidebar from '../../moleisms/user-sidebar'
import ProfilePage from '../user-profile'
import UserAlloys from '../../moleisms/user-alloys'
import UserSavedSimulations from '../../moleisms/user-sim'

import styles from './UserPage.module.scss'

class UserPage extends Component {
  /**
   * User page is a parent component that adds the `components/moleisms/UserSidebar
   * and a right panel with pages for user profile, alloys database, and saved
   * simulations.
   */
  redirect = () => {}

  render() {
    const { history, user } = this.props
    console.log(user)
    return (
      <React.Fragment>
        <AppBar active="user" redirect={history.push} />
        <div className={styles.sidebar}>
          {/* A sidebar with the sub navigation for the children components. */}
          <UserSidebar />
        </div>
        <div className={styles.main}>
          {/* Define the routes for the right panel. */}
          <Route path="/user/profile" render={props => <ProfilePage {...props} user={user} />} />
          <Route path="/user/alloys" render={props => <UserAlloys {...props} />} />
          <Route path="/user/simulations" render={props => <UserSavedSimulations {...props} />} />
        </div>
      </React.Fragment>
    )
  }
}

UserPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

const mapStateToProps = state => ({
  user: state.persist.user,
})

const mapDispatchToProps = {}

export default connect(mapStateToProps, mapDispatchToProps)(UserPage)
