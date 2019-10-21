/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AboutPage rendered by '/about'
 *
 * @version 1.0.0
 * @author Andrew Che
 *
 */
import React from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import AboutSidebar from '../../moleisms/about-sidebar'
import AboutApp from '../../moleisms/about-app'
import Disclaimer from '../../moleisms/about-disclaimer'
import Privacy from '../../moleisms/about-privacy'
import AboutAppBar from '../../moleisms/about-appbar'
// import AppBar from '../../moleisms/appbar'

import styles from './AboutPage.module.scss'

function AboutPage({ history }) {
  return (
    <>
      {/*<AppBar active="about" redirect={history.push} />*/}
      <AboutAppBar />

      <div className={styles.sidebar}>
        <AboutSidebar redirect={history.push} />
      </div>

      <div className={styles.main}>
        <Route path="/about/application" render={(props) => <AboutApp {...props} />} />
        <Route path="/about/disclaimer" render={(props) => <Disclaimer {...props} />} />
        <Route path="/about/privacy" render={(props) => <Privacy {...props} />} />
      </div>
    </>
  )
}

AboutPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

export default AboutPage
