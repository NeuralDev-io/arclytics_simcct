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
import Modal from '../../elements/modal/Modal'
import { passwordResetValidation } from '../../../utils/ValidationHelper'

import styles from './PasswordResetPage.module.scss'

//TODO: once the textfield err prop is fixed uncomment err and need just test edge cases 
//TOOD: propTypes

class PasswordResetPage extends Component {
  constructor(props){
    super(props)
    this.state = {
        newPwd: '',
        newPwdErr: '',
        cnfrmPwd: '',
        cnfrmPwdErr:'',
        showCnfrmModal: true,
        status: '',
    }
    this.handleStatus = this.handleStatus.bind(this)
  }

  handleStatus = () => {
    const { status, showCnfrmModal } = this.state
    console.log("[handleStatus]: ", status, (status === 'success'))
    if (status === ''){
      return ('')
    }
    if (status === 'success'){
      return( 
      <Modal className={styles.cnfrmModal} show={showCnfrmModal} > 
        <span>
          Your account password has been successfully changed. 
        </span>
        <Button length="long"onClick={() => {this.props.history.push('/signin')}}> Go to sign in </Button>
      </Modal>)
    } else {
      return (<span className={styles.error}>{status}</span>)
    }
  }

  handleSubmit = () => {
    console.log("handlesSubmit")
    const { match } = this.props
    const { newPwd, cnfrmPwd } = this.state
    const err = passwordResetValidation({newPwd, cnfrmPwd})
    if (!(
      Object.prototype.hasOwnProperty.call(err, 'newPwdErr') || 
      Object.prototype.hasOwnProperty.call(err, 'cnfrmPwdErr'))){
        const promise = new Promise((resolve, reject) => {
          resetPassword( 
            resolve,
            reject,
            { 
              password: newPwd, 
              confirm_password: cnfrmPwd, 
            }, 
            match.params.token,)
        })
        promise.then((data) => {
          //success
          this.setState({
            status: 'success'
          })
          // history.push('/signin') //TODO: uncomment when done  
        })
        .catch((err) => {
          console.log(err)
          this.setState({
            status: err,
          })
        })
    } else {
      this.setState({
        newPwdErr: Object.prototype.hasOwnProperty.call(err, 'newPwdErr') ? err.newPwdErr: (''),
        cnfrmPwdErr:Object.prototype.hasOwnProperty.call(err, 'cnfrmPwdErr') ? err.cnfrmPwdErr :('')
      })
    }
  }

  handleChange = (name, value) => {
      this.setState({
          [name]: value,
      })
  }

  render(){
    const { 
      newPwd,
      newPwdErr,
      cnfrmPwd,
      cnfrmPwdErr,
      status
    } = this.state
    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          <Logo className={styles.logo} />
          <h3> ARCLYTICS </h3>
        </div>
        <form className={styles.form}>
          <h3 className={styles.header}> Change Password </h3> 
          <TextField 
            type="password"
            name="newPwd"
            value={newPwd}
            placeholder="New Password"
            length="stretch"
            error = "test"
            error={newPwdErr}
            onChange={value => this.handleChange('newPwd', value)}
          />
          <TextField
            type="password"
            name="cnfrmPwd"
            value={cnfrmPwd}
            placeholder="Confirm Password"
            length="stretch"
            error = {cnfrmPwdErr}
            onChange={value => this.handleChange('cnfrmPwd', value)}
          />
          {this.handleStatus()}
          <Button length="long" onClick={this.handleSubmit}> Reset Password </Button>
        </form>
      </div>
    )
  }
}

// PasswordResetPage.propTypes = {
//   match: 
// }

export default (PasswordResetPage)