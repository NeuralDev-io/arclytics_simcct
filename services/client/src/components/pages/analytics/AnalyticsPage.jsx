/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AnalyticsPage rendered by '/analytics'
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import AppBar from '../../moleisms/appbar'
import AnalyticsSidebar from '../../moleisms/analytics-sidebar'
import UsersAnalytics from '../../moleisms/analytics-users'

import styles from './AnalyticsPage.module.scss'

function AnalyticsPage({ history }) {
  return (
    <>
      <AppBar active="analytics" redirect={history.push} isAdmin isAuthenticated />

      <div className={styles.sidebar}>
        <AnalyticsSidebar />
      </div>

      <div className={styles.main}>
        <Route path="/analytics/users" render={props => <UsersAnalytics {...props} />} />
      </div>

    </>
  )
}

AnalyticsPage.propTypes = {
  history: PropTypes.shape(
    { push: PropTypes.func.isRequired }
  ).isRequired
}

export default AnalyticsPage
