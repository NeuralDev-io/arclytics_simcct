import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import { connect } from 'react-redux'

import AppBar from '../../moleisms/appbar'
import UserSidebar from '../../moleisms/user-sidebar'
import ProfilePage from '../profile'
import UserAlloys from '../../moleisms/user-alloys'
import UserSavedSimulations from '../../moleisms/user-sim'

import styles from './UserPage.module.scss'

class UserPage extends Component {
  redirect = () => {}

  render() {
    const { history } = this.props

    return (
      <React.Fragment>
        <AppBar active="user" redirect={history.push} />
        <div className={styles.sidebar}>
          <UserSidebar />
        </div>
        <div className={styles.main}>
          <Route path="/user/profile" render={props => <ProfilePage {...props} />} />
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

// const mapStateToProps = state => ({
//   user: state.persist.user,
// })

// const mapDispatchToProps = {}

// export default connect(mapStateToProps, mapDispatchToProps)(UserPage)
export default UserPage
