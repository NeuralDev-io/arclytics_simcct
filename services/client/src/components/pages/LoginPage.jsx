import React, { Component } from 'react'
import { connect } from 'react-redux'

class LoginPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div>
        Login page here.
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
