import React from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import AppBar from '../../moleisms/appbar'
import AdminSidebar from '../../moleisms/admin-sidebar'
import ManageUsers from '../../moleisms/admin-users'
import AdminAlloys from '../../moleisms/admin-alloys'

import styles from './AdminPage.module.scss'

const AdminPage = ({ history }) => (
  <React.Fragment>
    <AppBar active="admin" redirect={history.push} isAdmin />
    <div className={styles.sidebar}>
      <AdminSidebar />
    </div>
    <div className={styles.main}>
      <Route path="/admin/alloys" render={props => <AdminAlloys {...props} />} />
      <Route path="/admin/users" render={props => <ManageUsers {...props} />} />
    </div>
  </React.Fragment>
)

AdminPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

export default AdminPage
