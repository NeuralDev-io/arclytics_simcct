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

import styles from './PasswordResetPage.module.scss'


class PasswordResetPage extends Component {
    constructor(props){
        super(props)
        this.state = {
            newPwd: '',
            cnfrmPwd: '',
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
        

        //TODO: promise
        resetPassword({ 
            password: newPwd, 
            confirm_password: cnfrmPwd, 
        }, match.params.token)
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
                        onChange={value => this.handleChange('newPwd', value)}
                    />
                    <TextField
                        type="password"
                        name="cnfrmPwd"
                        value={cnfrmPwd}
                        placeholder="Confirm Password"
                        length="stretch"
                        onChange={value => this.handleChange('cnfrmPwd', value)}
                    />
                    <Button length="long" onClick={this.handleSubmit}> Reset Password </Button>
                </div>
               
            </div>
        )
    }
}

export default (PasswordResetPage)