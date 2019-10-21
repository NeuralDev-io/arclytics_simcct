/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Feedback page for Admins rendered by '/feedback'
 *
 * @version 1.0.0
 * @author Andrew Che
 */
import React from 'react'
import PropTypes from 'prop-types'
import AppBar from '../../moleisms/appbar'
import AdminFeedback from '../../moleisms/admin-feedback'

import styles from './FeedbackPage.module.scss'

const FeedbackPage = ({ history, isAdmin }) => (
  <>
    <AppBar active="feedback" redirect={history.push} isAdmin={isAdmin} isAuthenticated />
    <div className={styles.main}>
      <AdminFeedback history={history} />
    </div>
  </>
)

FeedbackPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
}

export default FeedbackPage
