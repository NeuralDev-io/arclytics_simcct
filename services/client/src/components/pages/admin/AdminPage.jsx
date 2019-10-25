/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AdminPage rendered by '/admin'
 *
 * @version 1.1.0
 * @author Dalton Le, Andrew Che
 */
/* eslint-disable react/jsx-props-no-spreading */
import React from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import AppBar from '../../moleisms/appbar'
import AdminSidebar from '../../moleisms/admin-sidebar'
import ManageUsers from '../../moleisms/admin-users'
import AdminAlloys from '../../moleisms/admin-alloys'

import styles from './AdminPage.module.scss'

const AdminPage = ({ history }) => (
  <>
    <AppBar active="admin" redirect={history.push} isAdmin isAuthenticated />
    <div className={styles.sidebar}>
      <AdminSidebar redirect={history.push} />
    </div>
    <div className={styles.main}>
      <Route path="/admin/alloys" render={props => <AdminAlloys {...props} />} />
      <Route path="/admin/users" render={props => <ManageUsers {...props} />} />
    </div>
  </>
)

AdminPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

export default AdminPage
