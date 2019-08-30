import React, { Component } from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserSavedSimulations from '../../moleisms/user-sim'

import styles from './UserSimulationPage.module.scss'

class UserSimulationPage extends Component {
  render() {
    const { history } = this.props
    return (
      <React.Fragment>
        <AppBar active="savedSimulations" redirect={history.push} />
        <div className={styles.main}>
          <UserSavedSimulations />
        </div>
      </React.Fragment>
    )
  }
}

UserSimulationPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
}

export default UserSimulationPage
