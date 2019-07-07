import React, { Component } from 'react'
import { connect } from 'react-redux'
import Button from '../atoms/button'

class LoginPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div>
        Login page here.
        <Button onClick={() => {}}>Click me</Button>
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
