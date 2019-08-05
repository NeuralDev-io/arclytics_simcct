import React from 'react'
import Button from '../../elements/button'

const Restricted = props => (
  <div>
    Not allowed.
    <Button onClick={() => props.history.push('/')}>GO HOME</Button> {/* eslint-disable-line */}
  </div>
)

export default Restricted
