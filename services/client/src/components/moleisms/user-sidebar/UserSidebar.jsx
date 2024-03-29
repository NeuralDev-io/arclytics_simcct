/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * User sidebar.
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link, withRouter } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/pro-light-svg-icons/faUser'
import { faDatabase } from '@fortawesome/pro-light-svg-icons/faDatabase'
import { faSlidersV } from '@fortawesome/pro-light-svg-icons/faSlidersV'
import { faHeart } from '@fortawesome/pro-light-svg-icons/faHeart'
import Button from '../../elements/button'
import { updateFeedback } from '../../../state/ducks/feedback/actions'

import styles from './UserSidebar.module.scss'

class UserSidebar extends Component {
  constructor(props) {
    super(props)
    // We get the URL from the current window object and split on '/'
    const pathArr = window.location.pathname.split('/')

    this.state = {
      // Get the last element which is basically the same ID name in the below defined
      // navigation links to set the className style on it to make it `active`
      active: pathArr[pathArr.length - 1],
    }
  }

  handleOpenFeedback = () => {
    const { updateFeedbackConnect } = this.props
    updateFeedbackConnect({
      feedbackVisible: true,
      backdrop: true,
      givingFeedback: true,
    })
  }

  componentDidUpdate = (prevProps) => {
    const { location } = this.props
    if (prevProps.location !== location) {
      const pathArr = location.pathname.split('/')
      this.setState({
        active: pathArr[pathArr.length - 1],
      })
    }
  }

  render() {
    const { active } = this.state
    return (
      <div className={styles.sidebar}>
        <h4>Account</h4>
        <Link
          id="profile"
          to="/user/profile"
          className={`${styles.item} ${active === 'profile' && styles.active}`}
        >
          <FontAwesomeIcon icon={faUser} className={styles.icon} />
          <span>Profile</span>
        </Link>
        <Link
          id="security"
          to="/user/security"
          className={`${styles.item} ${active === 'security' && styles.active}`}
        >
          <FontAwesomeIcon icon={faDatabase} className={styles.icon} />
          <span>Security</span>
        </Link>
        <Link
          id="data-personalisation"
          to="/user/data-personalisation"
          className={`${styles.item} ${active === 'data-personalisation' && styles.active}`}
        >
          <FontAwesomeIcon icon={faSlidersV} className={styles.icon} />
          <span>Data personalisation</span>
        </Link>
        <Button
          appearance="text"
          length="long"
          IconComponent={props => <FontAwesomeIcon icon={faHeart} {...props} />}
          className={styles.feedbackButton}
          onClick={this.handleOpenFeedback}
        >
          Give feedback
        </Button>
      </div>
    )
  }
}

UserSidebar.propTypes = {
  updateFeedbackConnect: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string,
  }).isRequired,
}

const mapDispatchToProps = {
  updateFeedbackConnect: updateFeedback,
}

export default withRouter(connect(null, mapDispatchToProps)(UserSidebar))
