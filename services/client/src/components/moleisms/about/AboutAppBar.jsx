/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AppBar component
 *
 * @version 1.0.0
 * @author Dalton Le, Andrew Che, Arvy Salazar
 *
 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { ReactComponent as ANSTOLogo } from '../../../assets/ANSTO_Logo_SVG/logo.svg'
import { ReactComponent as LogoLight } from '../../../assets/logo_20.svg'
import { ReactComponent as LogoDark } from '../../../assets/logo_20_dark.svg'

import styles from './AboutAppBar.module.scss'

const AboutAppBar = ({ theme }) => (
  <nav className={styles.navContainer}>
    <div>
      <ANSTOLogo className={styles.anstoLogo} />
    </div>
    <div>
      {
        theme === 'light'
          ? <LogoLight className={styles.logo} />
          : <LogoDark className={styles.logo} />
      }
    </div>
  </nav>
)

AboutAppBar.propTypes = {
  theme: PropTypes.string.isRequired,
}

const mapStateToProps = (state) => ({
  theme: state.self.theme,
})

export default connect(mapStateToProps, {})(AboutAppBar)
