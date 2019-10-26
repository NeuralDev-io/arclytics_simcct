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
import { ReactComponent as ANSTOLogo } from '../../../assets/ANSTO_Logo_SVG/logo.svg'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'

import styles from './AboutAppBar.module.scss'

const AboutAppBar = () => (
  <nav className={styles.navContainer}>
    <div>
      <ANSTOLogo className={styles.anstoLogo} />
    </div>
    <div>
      <Logo className={styles.logo} />
    </div>
  </nav>
)

export default AboutAppBar
