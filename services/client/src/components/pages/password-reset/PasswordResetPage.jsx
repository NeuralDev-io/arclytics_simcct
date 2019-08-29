/**
 * Login Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */

import React, { Component } from 'react'
import { resetPassword } from '../../../utils/AuthenticationHelper'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'

import PropTypes from 'prop-types'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import { passwordResetValidation } from '../../../utils/ValidationHelper'

import styles from './PasswordResetPage.module.scss'

//TODO: once the textfield err prop is fixed uncomment err and need just test edge cases 

class PasswordResetPage extends Component {
  constructor(props){
      super(props)
      this.state = {
          newPwd: '',
          newPwdErr: '',
          cnfrmPwd: '',
          cnfrmPwdErr:'',
      }
  }

  componentDidMount = () => {
      const { match, history } = this.props
      console.log(match.params.token)
      if(!match.params.token) {
          history.push('/signin') //TODO: not working
      }
  }

  handleSubmit = () => {
    console.log("handlesSubmit")
    const { match } = this.props
    const { newPwd, cnfrmPwd } = this.state
    //TODO: do validation here
    const err = passwordResetValidation({newPwd, cnfrmPwd})
   
    //TODO: create a promise here to make sure and handle errors correctly 
      resetPassword(
        { 
        password: newPwd, 
        confirm_password: cnfrmPwd, 
        }, 
        match.params.token,)
      //TODO: redirect to sign in 
  }

  handleChange = (name, value) => {
      this.setState({
          [name]: value,
      })
  }

  render(){
    const { newPwd, cnfrmPwd } = this.state
    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          <Logo className={styles.logo} />
          <h3> ARCLYTICS </h3>
        </div>
        <div className={styles.form}>
          <h3 className={styles.header}> Change Password </h3> 
          <TextField 
            type="password"
            name="newPwd"
            value={newPwd}
            placeholder="New Password"
            length="stretch"
            //err={newPwdErr}
            onChange={value => this.handleChange('newPwd', value)}
          />
          <TextField
            type="password"
            name="cnfrmPwd"
            value={cnfrmPwd}
            placeholder="Confirm Password"
            length="stretch"
            //err={cnfrmPwd}
            onChange={value => this.handleChange('cnfrmPwd', value)}
          />
          <Button length="long" onClick={this.handleSubmit}> Reset Password </Button>
        </div>
      </div>
    )
  }
}

// PasswordResetPage.propTypes = {
//   match: 
// }

export default (PasswordResetPage)