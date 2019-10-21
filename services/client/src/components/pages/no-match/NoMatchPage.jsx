/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AdminPage rendered by '/admin'
 *
 * @version 1.0.0
 * @author Arvy Salazar
 */
import React from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import { ReactComponent as PageNotFoundImage } from '../../../assets/undraw_page_not_found_su7k.svg'

import styles from './NoMatchPage.module.scss'

const NoMatchPage = ({ history, location }) => (
  <div>
    <div className={styles.container}>
      <PageNotFoundImage className={styles.pageNotFoundImage} />
      <h3>
        The URL <code>{location.pathname}</code> doesn&apos;t exist in our server.
      </h3>
      <div className={styles.buttonContainer}>
        <Button onClick={() => history.goBack()}>Go back</Button>
        <Button onClick={() => history.push('/')}>Go home</Button>
      </div>
    </div>
  </div>
)

NoMatchPage.propTypes = {
  history: PropTypes.string.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
}

export default NoMatchPage
