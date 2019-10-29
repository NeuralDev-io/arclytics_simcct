/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * About Sidebar
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUserShield } from '@fortawesome/pro-light-svg-icons/faUserShield'
import { faInfoSquare } from '@fortawesome/pro-light-svg-icons/faInfoSquare'
import { faExclamationTriangle } from '@fortawesome/pro-light-svg-icons/faExclamationTriangle'
import { faHeart } from '@fortawesome/pro-light-svg-icons/faHeart'
import { faArrowLeft } from '@fortawesome/pro-light-svg-icons/faArrowLeft'
import Button from '../../elements/button'

import styles from './AboutSidebar.module.scss'

class AboutSidebar extends Component {
  constructor(props) {
    super(props)
    const pathArr = window.location.pathname.split('/')
    this.state = {
      active: pathArr[2],
    }
  }

  componentDidMount = () => {
    const { active } = this.state
    const { redirect } = this.props
    if (!['application', 'disclaimer', 'privacy', 'acknowledgements'].includes(active)) {
      this.setState({ active: 'application' })
      redirect('/about/application')
    }
  }

  handleRedirect = (route) => {
    this.setState({ active: route })
    document.getElementById('app').scrollTop = 0
  }

  handleBackToApp = () => {
    const { redirect, from } = this.props
    redirect(from)
  }

  render() {
    const { active } = this.state
    const { from } = this.props
    return (
      <div className={styles.sidebar}>
        <h4>More information</h4>
        {/*
          Link components will redirect to correct about section but will persist
          the 'from' location so that when user clicks on "Back to app" in
          AboutSidebar they will go to the previous route before they went to
          '/about/...'
        */}
        <Link
          id="application"
          to={{
            pathname: '/about/application',
            state: { from },
          }}
          onClick={() => this.handleRedirect('application')}
          className={`${styles.item} ${active === 'application' && styles.active}`}
        >
          <FontAwesomeIcon icon={faInfoSquare} className={styles.icon} />
          <span>Arclytics SimCCT</span>
        </Link>
        <Link
          id="disclaimer"
          to={{
            pathname: '/about/disclaimer',
            state: { from },
          }}
          onClick={() => this.handleRedirect('disclaimer')}
          className={`${styles.item} ${active === 'disclaimer' && styles.active}`}
        >
          <FontAwesomeIcon icon={faExclamationTriangle} className={styles.icon} />
          <span>Disclaimer</span>
        </Link>
        <Link
          id="privacy"
          to={{
            pathname: '/about/privacy',
            state: { from },
          }}
          onClick={() => this.handleRedirect('privacy')}
          className={`${styles.item} ${active === 'privacy' && styles.active}`}
        >
          <FontAwesomeIcon icon={faUserShield} className={styles.icon} />
          <span>Privacy policy</span>
        </Link>
        <Link
          id="privacy"
          to={{
            pathname: '/about/acknowledgements',
            state: { from },
          }}
          onClick={() => this.handleRedirect('acknowledgements')}
          className={`${styles.item} ${active === 'acknowledgements' && styles.active}`}
        >
          <FontAwesomeIcon icon={faHeart} className={styles.icon} />
          <span>Acknowledgements</span>
        </Link>
        <Button
          appearance="text"
          length="long"
          IconComponent={props => <FontAwesomeIcon icon={faArrowLeft} {...props} />}
          className={styles.back}
          onClick={this.handleBackToApp}
        >
          Back to app
        </Button>
      </div>
    )
  }
}

AboutSidebar.propTypes = {
  redirect: PropTypes.func.isRequired,
  from: PropTypes.string.isRequired,
}

export default AboutSidebar
