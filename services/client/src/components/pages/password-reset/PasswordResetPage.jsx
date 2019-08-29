import React, { Component } from 'react'
import styles from './PasswordResetPage.module.scss'

import TextField from '../../elements/textfield'
import Button from '../../elements/button'

class PasswordResetPage extends Component {

    componentDidMount = () => {
        const { match,history } = this.props

        // TODO: fix this later to redirect back to signin
        if(!match.params.token){
            history.push('/signin')
        }
    }

    render(){
        const { match } = this.props
        return (
            <div>
                <TextField 
                    type="password"
                    name="newPwd"
                    placeholder="New Password"
                    length="long"
                    
                />
                <TextField
                    type="password"
                    name="cnfrmPwd"
                    placeholder="Confirm Password"
                    length="long"
                />
                <Button />

                {/* {match.params.token} */}
            </div>
        )
    }
}

export default (PasswordResetPage)