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
import {
  AboutApp,
  AboutAppBar,
  AboutSidebar,
  Privacy,
  Disclaimer,
  Acknowledgements,
} from '../../moleisms/about'

import styles from './AboutPage.module.scss'

function AboutPage({ history, location }) {
  const { state = { from: '' } } = location
  console.log(state.from)
  return (
    <>
      <AboutAppBar />

      <div className={styles.sidebar}>
        <AboutSidebar redirect={history.push} from={state.from} />
      </div>

      <div className={styles.main} id="about-content">
        <Route path="/about/application" render={(props) => <AboutApp {...props} />} />
        <Route path="/about/disclaimer" render={(props) => <Disclaimer {...props} />} />
        <Route path="/about/privacy" render={(props) => <Privacy {...props} />} />
        <Route path="/about/acknowledgements" render={(props) => <Acknowledgements {...props} />} />
      </div>
    </>
  )
}

AboutPage.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape({
      from: PropTypes.string.isRequired,
    }),
  }).isRequired,
}

export default AboutPage
