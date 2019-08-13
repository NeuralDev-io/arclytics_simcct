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
      email: props.user.email,
      firstName: props.user.first_name, //just in case we implement demo mode
      lastName: props.user.last_name,
      question1:  props.user.profile ? { label:props.user.profile.aim , value: props.user.profile.aim } : null,
      question1Select: [
        { label: 'Option 1', value: 'Option 1'},
        { label: 'Option 2', value: 'Option 2'},
      ],
      question2: props.user.profile ? { label:props.user.profile.sci_tech_exp , value: props.user.profile.sci_tech_exp } : null,
      question2Select: [
        { label: 'Option 1', value: 'Option 1'},
        { label: 'Option 2', value: 'Option 2'},
      ],
      question3: props.user.profile ? { label:props.user.profile.phase_transform_exp , value: props.user.profile.phase_transform_exp } : null,
      question3Select: [
        { label: 'Option 1', value: 'Option 1'},
        { label: 'Option 2', value: 'Option 2'},
      ],
      currPassword: null,
      newPassword: null,
      cnfrmPassword: null,
      showDelete: false,
      edit: false,
    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem("token"))
      this.props.history.push('/signin')
  }

  handleDeleteModal = () => {
    this.state.showDelete ? this.setState({showDelete: false}) : this.setState({showDelete: true}) 
  }

  
  handleEdit = () => {
    const { user } = this.props
    this.state.edit ? 
    this.setState({
      firstName: user.first_name, //just in case we implement demo mode
      lastName: user.last_name,
      question1:  user.profile ? {label:user.profile.aim , value:user.profile.aim} : null,
      question2: user.profile ? {label:user.profile.sci_tech_exp , value: user.profile.sci_tech_exp} : null,
      question3: user.profile ? {label:user.profile.phase_transform_exp , value: user.profile.phase_transform_exp} : null,
      edit: false
    }) 
    :   
      this.setState({edit: true}) 
  }


  handleChange = (name, value) => {
    this.setState({
      [name]: value
    })
  }

  updateUser = () => {
    const {firstName, lastName, question1, question2, question3} = this.state
    this.props.updateUserProfileConnect({
      first_name: firstName,
      last_name: lastName,
      profile:{
        aim: question1 ? question1.value : null,
        sci_tech_exp: question2 ? question2.value : null,
        phase_transform_exp: question3 ? question3.value : null
      }
    })
    this.setState({ edit: false })
  }

  render() {
    const { 
      firstName,
      lastName,
      email,
      question1,
      question1Select,
      question2,
      question2Select,
      question3,
      question3Select,
      currPassword, 
      newPassword, 
      cnfrmPassword, 
      showDelete,
      edit,
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
            <div className={styles.generalFields}>
              <div className={styles.row}>
                <h6 className={styles.column}> Email </h6> 
                <div className={styles.column}> <h6 className={styles.emailText}> {email} </h6> </div>   
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
                    isDisabled={!edit}
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
                  isDisabled={!edit}
                  onChange={value => this.handleChange('lastName', value )}
                />
              </div> 
            </div>     
            </div>
       
            <div className={styles.profilePicture}> Profile Picture </div>
          </div>
       
          <div className={styles.about}>
            <h4 className={styles.header}> About yourself </h4>
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
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question1', value )}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}> What is your experience with solid-state phase transformation?  </h6>
                <Select
                  type="question2"
                  name="question2"
                  placeholder="---"
                  value= {question2}
                  options={question2Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question2', value )}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}> What is your experiece with scientific software? </h6>
                <Select
                  type="question2"
                  name="question2"
                  placeholder="---"
                  value= {question3}
                  options={question3Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question3', value )}
                />
              </div>
            </div>
          </div>
          
          <div>
              {!edit ? ( <div className={styles.editButtons}> <Button onClick={this.handleEdit}> Edit </Button> </div>) : ('')} 
              {edit ? (
              <div className={styles.editButtons}> 
                <Button onClick={this.updateUser}> Save </Button>
                <Button className={styles.cancel}appearance="outline" onClick={this.handleEdit}> Cancel </Button> 
              </div>) : ('')} 
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

