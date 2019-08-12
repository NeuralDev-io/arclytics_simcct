/**
 * Profile Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { updateUserProfile } from '../../../state/ducks/persist/actions'

import TextField from '../../elements/textfield'
import Select from '../../elements/select'
import AppBar from '../../moleisms/appbar'
import Modal from '../../elements/modal'
import Button from '../../elements/button'

import styles from './ProfilePage.module.scss'

class ProfilePage extends Component {
  constructor(props){
    super(props)
     /*
        check if profile is null before accessing it 
        https://stackoverflow.com/questions/51206488/how-to-set-component-state-conditionally
    */
    this.state = {
      email: "example@example.com",
      firstName: props.user.first_name, //just in case we implement demo mode
      lastName: props.user.last_name,
      occOptions:[
        { label: 'Student', value: 'student'},
        { label: 'Work', value: 'work'},
      ],
      occupation: null,
      eduOptions: [
        { label: 'Be a man training montage', value: 'opt21'},
        { label: 'Option 2', value: 'opt22'},
      ],
      question1: null,
      question1Select: [
        { label: 'To defeat the huns', value: 'opt11'},
        { label: 'Option 2', value: 'opt12'},
      ],
      question2: null,
      question2Select: [
        { label: 'Be a man training montage', value: 'opt21'},
        { label: 'Option 2', value: 'opt22'},
      ],
      question3: null,
      question3Select: [
        { label: 'Swords', value: 'opt31'},
        { label: 'Option 2', value: 'opt32'},
      ],
      education: props.user.profile ? { label:props.user.profile.highest_education , value: 'opt21'} : null,
      currPassword: null,
      newPassword: null,
      cnfrmPassword: null,
      showDelete: false,
    }
  }

  componentDidUpdate = (prevState) => {
    const {firstName, lastName, occOptions } = this.state
    //Checks for changes
    if (this.state.firstname !== prevState.firstName) {
      this.props.updateUserProfileConnect({
        "firstName": firstName 
      })
    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem("token"))
      this.props.history.push('/signin')
  }

  handleDeleteModal = () => {
    this.state.showDelete ? this.setState({showDelete: false}) : this.setState({showDelete: true}) 
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value
    })
  }

  // handleOnBlur = (name, value) => {
  //   this.state[name]
  // }

  render() {
    const { 
      firstName,
      lastName,
      question1,
      question1Select,
      question2,
      question2Select,
      question3,
      question3Select,
      question4,
      question4Select, 
      currPassword, 
      newPassword, 
      cnfrmPassword, 
      showDelete,
    } = this.state
    const { user } = this.props
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
          <div className={styles.general}>
            <h4 className={styles.header}>General</h4>
            <div className={styles.row}>
              <h6 className={styles.column}> Email </h6> 
              <div className={styles.column}> <h6 className={styles.emailText}> {user.email} </h6> </div>   
            </div>
            <div className={styles.row}>
              <h6  className={styles.leftCol}>First name</h6>
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
                <h6 className={styles.column}> Last name </h6>
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
            </div>
       

          <div className={styles.about}>
            <h4> About yourself </h4>
            <div className={styles.questions}>
              <div className={styles.question}>
                <h6 className={styles.questionText}> What sentence best describes you? </h6>
                <Select
                  type="question1"
                  name="question1"
                  placeholder="---"
                  value= {question1}
                  options={question1Select}
                  length="stretch"
                  onChange={value => this.handleChange('question1', value )}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}> What sentence best describes you? </h6>
                <Select
                  type="question2"
                  name="question2"
                  placeholder="---"
                  value= {question2}
                  options={question2Select}
                  length="stretch"
                  onChange={value => this.handleChange('question2', value )}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}> What sentence best describes you? </h6>
                <Select
                  type="question2"
                  name="question2"
                  placeholder="---"
                  value= {question3}
                  options={question3Select}
                  length="stretch"
                  onChange={value => this.handleChange('question3', value )}
                />
              </div>
            </div>
          </div>

          <div className={styles.security}>
            <h4 className={styles.header}>Security</h4>
            <h5>Change your password</h5>
            <div className={styles.row}>
              <h6 className={styles.currPwd}>Current password</h6>
              <div className={StyleSheet.input}>
                <TextField
                  type="password"
                  name="currPassword"
                  placeholder="Current Password"
                  value = {currPassword}
                  length="long"
                  onChange={value => this.handleChange('currPassword', value)}
                />
              </div>
            </div>

            <div className={styles.row}>
              <h6 className={styles.newPwd}>New password</h6>
              <div className={styles.input}>
                <TextField
                    type="password"
                    name="newPassword"
                    placeholder="Confirm Password"
                    value= {newPassword}
                    length="long"
                    onChange={value => this.handleChange('newPassword', value)}
                />  
              </div>
            </div>

            <div className={styles.row}>
             <h6 className={styles.cnfrmPwd}>Confirm password</h6> 
             <div className={styles.input}>
              <TextField
                  type="password"
                  name="cnfrmPassword"
                  placeholder="Confirm Password"
                  value= {cnfrmPassword}
                  length="long"
                  onChange={value => this.handleChange('cnfrmPassword', value)}
                />
             </div>
            </div>
          </div>

          <div>
            <h5 className={styles.deleteWarning}>Delete your account</h5>
            <h6 className={styles.deleteWarning}>Once you delete your account, there is no going back. Please be certain</h6>
            <h6 className={styles.delete} onClick={this.handleDeleteModal}>Delete my account</h6>  
            <Modal  show={showDelete} clicked={this.handleDeleteModal}> 
              <div className={styles.deleteModal} >
              <h6>All of your data will be lost. Are you sure you want to delete your account? Please enter your password to confirm</h6>
              <TextField
                type="password"
                name="cnfrmDelete"
                placeholder="Enter Password"
                length="stretch"
                onChange={value => this.handleChange('cnfrmDelete', value)}
              />
                <div className={styles.deleteButtons}>
                  <Button className={styles.cancelDelete} name="cancelDelete" type="button" onClick={this.handleDeleteModal} length="long">
                    CANCEL
                  </Button> 
                  <h6 className={styles.delete}> Delete my account </h6> 
                </div>
              </div>

            </Modal>
          </div>
        </div>
      </React.Fragment>
    )
  }
}

const mapStateToProps = state => ({
  user: state.persist.user
})

const mapDispatchToProps = {
  updateUserProfileConnect: updateUserProfile,
}

export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)

