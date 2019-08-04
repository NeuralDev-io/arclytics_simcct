/**
 * Profile Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'

import TextField from '../../elements/textfield'
import Button from '../../elements/button'
import AppBar from '../../moleisms/appbar'

import styles from './ProfilePage.module.scss'

class ProfilePage extends Component {
  constructor(props){
    super(props)
    this.state = {
      email: "arvy",
    };
  }
  componentDidMount = () => {
    // (arvy@neuraldev.io) - I done it this way https://stackoverflow.com/questions/35850118/setting-state-on-componentdidmount and https://reactjs.org/docs/faq-ajax.html

  }

  render() {
    return (
      <React.Fragment>
        <AppBar active="profile" redirect={this.props.history.push} /> 
        <div className={styles.Sidebar}>
          <h3>User Settings</h3>

          <div className={styles.navList}>
            <div> Account settings </div>
            <div> User Account </div>
          </div>
        </div>
        <div className={styles.main}> 
          <h4> General</h4>
          <div className={styles.generalColumn}>
            <div className={styles.generalRow}>
              Email <TextField
                type="email"
                name="email"
                value={this.props.email}
                placeholder="Email"
                length="stretch"
              />
            </div>
            <div className={styles.generalRow}>
              First name
            </div>
            <div className={styles.generalRow}>
              Last name
            </div>
            <div className={styles.generalRow}>
              Occupation
            </div>
            <div className={styles.generalRow}>
              Education
            </div>            
          </div>
          <h4>Security</h4>
          <h3>Change your password</h3>
          <div className={styles.securityColumn}>
            <div className={styles.securityRow}>
              Current password
            </div>
            <div className={styles.securityRow}>
              New password
            </div>
            <div className={styles.securityRow}>
              Confirm password
            </div>
          </div>
          <h3>Delete your account</h3>
          <div>Once you delete your account, there is no going back. Please be certain</div>
          <div>Delete my account</div>  
        </div>
      </React.Fragment>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
