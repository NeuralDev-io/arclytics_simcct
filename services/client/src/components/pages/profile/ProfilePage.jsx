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
import Select from '../../elements/select'
import AppBar from '../../moleisms/appbar'
import Modal from '../../elements/modal'

import styles from './ProfilePage.module.scss'

class ProfilePage extends Component {
  constructor(props){
    super(props)
    this.state = {
      email: "example@example.com",
      firstName: null,
      lastName: null,
      occOptions:[
        { label: 'Student', value: 'student'},
        { label: 'University', value: 'university'},
      ],
      occupation: { label: 'Student', value: 'student'},
      eduOptions: [
        { label: 'HighSchool', value: 'highSchool'},
        { label: 'University', value: 'university'},
      ],
      eduSelect: { label: 'HighSchool', value: 'highSchool'},
      showDelete: true,
    };
  }
  componentDidMount = () => {
    // (arvy@neuraldev.io) - I set state because of this  https://stackoverflow.com/questions/35850118/setting-state-on-componentdidmount and https://reactjs.org/docs/faq-ajax.html
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value
    })
  }

  render() {
    const { firstName, lastName, occupation, occOptions, education, eduOptions } = this.state

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
          <h4 className={styles.header}>General</h4>
          <div className={styles.general}>
            <div className={styles.row}>
            
            <h7 className={styles.column}> Email </h7> 
            <div className={styles.column}> <h7 className={styles.emailText}> {this.state.email} </h7> </div>  
           
            </div>
            <div className={styles.row}>
              <h7  className={styles.leftCol}>First name</h7>
              <div className={styles.column}>
                <TextField
                  type="firstName"
                  name="firstName"
                  value={firstName}
                  placeholder="First Name"
                  length="short"
                  onChange={value => this.handleChange('firstName', value)}
                />
              </div>
              
            </div>
            <div className={styles.row}>
              <h7 className={styles.column}> Last name </h7>
              <div className={styles.column}>
                <TextField
                  type="lastName"
                  name="lastName"
                  value={lastName}
                  placeholder="Last Name"
                  length="short"
                  onChange={value => this.handleChange('lastName', value )}
                />
              </div> 
            </div>
            <div className={styles.row}>
              <div className={styles.column}> <h7>Occupation</h7> </div>
              <div className={styles.column}>
                <Select
                  type="occupation"
                  name="occupation"
                  placeholder="Choose Occupation"
                  options={occOptions}
                  value={occupation}
                  length="long"
                  onChange={val => this.handleOccSelect(val)}
                />
              </div>
            </div>
            <div className={styles.row}>
              <div className={styles.column}><h7>Education</h7></div>
              <div className={styles.column}>  
              <Select
                name="education"
                placeholder="Choose Educaion"
                options={this.state.eduOptions}
                value={this.state.eduSelect}
                length="long"
                onChange={val => this.handleEduSelect(val)}/>
              </div>
            </div>

            <div className={styles.profilePicture}> a </div>         
          </div>
          <h4 className={styles.header}>Security</h4>
          <h3>Change your password</h3>
          <div className={styles.security}>
            <div className={styles.row}>
              <h7 className={styles.currPwd}>Current password</h7>
              <div className={StyleSheet.input}>
                <TextField
                  type="currentPassword"
                  name="currentPassword"
                  placeholder="Current Password"
                  length="long"
                />
              </div>
            </div>

            <div className={styles.row}>
              <h7 className={styles.newPwd}>New password</h7>
              <div className={styles.input}>
              <TextField
                type="newPassword"
                name="newPassword"
                placeholder="New Password"
                length="long"
              />
              </div>
            </div>

            <div className={styles.row}>
             <h7 className={styles.cnfrmPwd}>Confirm password</h7> 
             <div className={styles.input}>
              <TextField
                  type="confirmPassword"
                  name="confirmPassoword"
                  placeholder="Confirm Password"
                  length="long"
                />
             </div>
            </div>
          </div>
          <h3>Delete your account</h3>
       
          <div className={styles.deleteWarning}>Once you delete your account, there is no going back. Please be certain</div>
          <div className={styles.delete} onClick={this.state.showDelete}>Delete my account</div>  
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
