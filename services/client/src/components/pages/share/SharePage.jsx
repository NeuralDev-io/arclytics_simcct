import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { loadSimFromLink } from '../../../state/ducks/sim/actions'

class SharePage extends Component {
  componentDidMount = () => {
    const { match, loadSimFromLinkConnect, history } = this.props
    loadSimFromLinkConnect(match.params.token)
      .then(() => history.push('/'))
      .catch(err => console.log(err))
  }

  render() {
    return (
      <div>
        Please wait while we&apos;re getting your data...
      </div>
    )
  }
}

SharePage.propTypes = {
  loadSimFromLinkConnect: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string,
    }),
  }).isRequired,
  history: PropTypes.shape({
    push: PropTypes.func,
  }).isRequired,
}

const mapDispatchToProps = {
  loadSimFromLinkConnect: loadSimFromLink,
}

export default connect(null, mapDispatchToProps)(SharePage)
