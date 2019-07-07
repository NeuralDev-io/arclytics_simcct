import React, { Component } from 'react'
import { connect } from 'react-redux'

class SignupPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div>
        Signup page here.
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(SignupPage)
