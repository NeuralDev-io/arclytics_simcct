import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { ReactComponent as PageNotFoundImage } from '../../../assets/undraw_page_not_found_su7k.svg'

class NoMatchPage extends Component{
  render() {
    const { location } = this.props
    return (
      <div>
        <div>
          <PageNotFoundImage className={styles.pageNotFoundImage}/>
          <h3>
            No match for
            <code>{location.pathname}</code>
          </h3>
        </div>
        )
      </div>
    )
  }
}

NoMatchPage.propTypes = {
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }),
}

export default NoMatchPage
