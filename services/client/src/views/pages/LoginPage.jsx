import React, { Component } from 'react'
import { connect } from 'react-redux'
import Button from '../../lib/button'

class LoginPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div>
        <Button onClick={() => {}}>BUTTON</Button>
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
