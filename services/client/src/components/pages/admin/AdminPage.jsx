import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Restricted from '../../moleisms/restricted'

class AdminPage extends Component {
  redirect = () => {}

  render() {
    const { isAdmin } = this.props
    if (!isAdmin) return <Restricted />
    return (
      <div>
        Admin page
      </div>
    )
  }
}

AdminPage.propTypes = {
  isAdmin: PropTypes.bool.isRequired,
}

const mapStateToProps = state => ({
  isAdmin: state.persist.user.admin,
})

const mapDispatchToProps = {}

export default connect(mapStateToProps, mapDispatchToProps)(AdminPage)
