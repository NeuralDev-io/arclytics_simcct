import React from 'react'
import PropTypes from 'prop-types'
import Button from '../../elements/button'

const Restricted = ({ history }) => (
  <div>
    Not allowed.
    <Button onClick={() => history.push('/')}>GO HOME</Button> {/* eslint-disable-line */}
  </div>
)

Restricted.propTypes = {
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

export default Restricted
