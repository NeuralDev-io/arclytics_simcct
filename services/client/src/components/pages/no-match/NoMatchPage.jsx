import React, { Component } from 'react'
import PropTypes from 'prop-types'

class NoMatchPage extends Component{
  render() {
    const { location } = this.props
    return (
      <div>
        <div>
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
