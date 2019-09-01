import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import UserAlloys from '../../moleisms/user-alloys'

import styles from './UserAlloyPage.module.scss'

const UserAlloyPage = ({ history }) => (
  <React.Fragment>
    <AppBar active="userAlloys" redirect={history.push} />
    <div className={styles.main}>
      <UserAlloys />
    </div>
  </React.Fragment>
)

UserAlloyPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
}

export default UserAlloyPage
