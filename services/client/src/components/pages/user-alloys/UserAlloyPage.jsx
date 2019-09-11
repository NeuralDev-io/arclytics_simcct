import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserAlloys from '../../moleisms/user-alloys'

import styles from './UserAlloyPage.module.scss'

const UserAlloyPage = ({ history, isAdmin }) => (
  <React.Fragment>
    <AppBar active="userAlloys" redirect={history.push} isAdmin={isAdmin} />
    <div className={styles.main}>
      <UserAlloys history={history} />
    </div>
  </React.Fragment>
)

UserAlloyPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
}

export default UserAlloyPage
