/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * This page will be rendered on screens with width < 1366px
 *
 * @version 1.0.0
 * @author Dalton Le
 */
import React from 'react'
import { ReactComponent as DesktopImage } from '../../../assets/desktop_illustration.svg'

import styles from './MobilePage.module.scss'

const MobilePage = () => (
  <div className={styles.container}>
    <DesktopImage className={styles.desktopImage} />
    <h4>Arclytics SimCCT is only available on desktops at the moment.</h4>
  </div>
)

export default MobilePage
