import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Restricted from '../../moleisms/restricted'
import AppBar from '../../moleisms/appbar'
import AdminSidebar from '../../moleisms/admin-sidebar/AdminSidebar'

import styles from './AdminPage.module.scss'

class AdminPage extends Component {
  redirect = () => {}

  render() {
    const { isAdmin, history } = this.props

    if (!isAdmin) return <Restricted history={history} />
    return (
      <React.Fragment>
        <AppBar active="admin" redirect={history.push} />
        <div className={styles.sidebar}>
          <AdminSidebar />
        </div>
      </React.Fragment>
    )
  }
}

AdminPage.propTypes = {
  isAdmin: PropTypes.bool.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

const mapStateToProps = state => ({
  isAdmin: state.persist.user.admin,
})

const mapDispatchToProps = {}

export default connect(mapStateToProps, mapDispatchToProps)(AdminPage)
