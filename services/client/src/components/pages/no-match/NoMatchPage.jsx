import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'
import { ReactComponent as PageNotFoundImage } from '../../../assets/undraw_page_not_found_su7k.svg'

import styles from './NoMatchPage.module.scss'

class NoMatchPage extends Component {
  render() {
    const { history, location } = this.props
    return (
      <div>
        <div className={styles.container}>
          <PageNotFoundImage className={styles.pageNotFoundImage}/>
          <h3>
            The URL <code>{location.pathname}</code> doesn&apos;t exist in our server.
          </h3>
          <div className={styles.buttonContainer}>
            <Button onClick={() => history.goBack()}>Go back</Button>
            <Button onClick={() => history.push('/')}>Go home</Button>
          </div>
        </div>
        )
      </div>
    )
  }
}

NoMatchPage.propTypes = {
  history: PropTypes.string.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }),
}

export default NoMatchPage
