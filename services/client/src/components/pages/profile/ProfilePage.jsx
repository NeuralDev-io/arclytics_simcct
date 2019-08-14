/**
 * Profile Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { createUserProfile, updateUserProfile } from '../../../state/ducks/persist/actions'

import TextField from '../../elements/textfield'
import Select from '../../elements/select'
import AppBar from '../../moleisms/appbar'
import Button from '../../elements/button'
import MailIcon from 'react-feather/dist/icons/mail'

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
        { label: 'Q1 Option 1', value: 'Q1 Option 1'},
        { label: 'Q1 Option 2', value: 'Q1 Option 2'},
      ],
      question2: props.user.profile ? { label:props.user.profile.highest_education , value: props.user.profile.highest_education } : null,
      question2Select: [
        { label: 'Q2 Option 1', value: 'Q2 Option 1'},
        { label: 'Q2 Option 2', value: 'Q2 Option 2'},
      ],
      question3: props.user.profile ? { label:props.user.profile.sci_tech_exp , value: props.user.profile.sci_tech_exp } : null,
      question3Select: [
        { label: 'Q3 Option 1', value: 'Q3 Option 1'},
        { label: 'Q3 Option 2', value: 'Q3 Option 2'},
      ],
      question4: props.user.profile ? { label:props.user.profile.phase_transform_exp , value: props.user.profile.phase_transform_exp } : null,
      question4Select: [
        { label: 'Q4 Option 1', value: 'Q4 Option 1'},
        { label: 'Q4 Option 2', value: 'Q4 Option 2'},
      ],
      updateError: null,
      edit: false,

    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem("token"))
      this.props.history.push('/signin')
  }

  handleEdit = () => {
    const { user } = this.props
    this.state.edit ? 
    this.setState({
      firstName: user.first_name, //just in case we implement demo mode
      lastName: user.last_name,
      question1:  user.profile ? {label:user.profile.aim , value:user.profile.aim} : null,
      question2: user.profile ? {label:user.profile.highest_education, value: user.profile.highest_education} : null,
      question3: user.profile ? {label:user.profile.sci_tech_exp , value: user.profile.sci_tech_exp} : null,
      question4: user.profile ? {label:user.profile.phase_transform_exp , value: user.profile.phase_transform_exp} : null,
      edit: false,
      updateError: null 
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
    const {firstName, lastName, question1, question2, question3, question4} = this.state
    const { user } = this.props

    if (!user.profile){
      if (!(question1 && question2 && question3 && question4)){
        this.setState({
          updateError: "Must answer all questions to save"
        })
      } 
      else if (question1 && question2 && question3 && question4){
        this.props.createUserProfileConnect({
          aim: question1.value, 
          highest_education: question2.value, 
          sci_tech_exp: question3.value, 
          phase_transform_exp: question4.value
        })
        this.props.updateUserProfileConnect({
          first_name: firstName,
          last_name: lastName,
        })
        this.setState({ edit: false, updateError: null })
      }      
    } else if (user.profile){
      this.props.updateUserProfileConnect({
        first_name: firstName,
        last_name: lastName,
          aim: question1 ? question1.value : null,
          highest_education: question2 ? question2.value: null,
          sci_tech_exp: question2 ? question3.value : null,
          phase_transform_exp: question3 ? question4.value : null
      })
      this.setState({ edit: false, updateError: null })
    }
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
      question4,
      question4Select,
      updateError,
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
          
          <React.Fragment>
            <h4 className={styles.header}>General</h4>
            <div className={styles.generalFields}>
              <div className={styles.row}>
                <h6 className={styles.leftCol}> Email </h6> 
                <div className={styles.rightCol}> <h6 className={styles.emailText}> {email} </h6> </div>   
              </div>
              <div className={styles.row}>
                <h6  className={styles.leftCol}>First name</h6>
                <div className={styles.rightCol}>
                <TextField
                    type="firstName"
                    name="firstName"
                    value={firstName}
                    placeholder="First Name"
                    length="stretch"
                    isDisabled={!edit}
                    onChange={value => this.handleChange('firstName', value)}
                  />
                </div>       
                </div>
              <div className={styles.row}>
              <h6 className={styles.leftCol}> Last name </h6>
              <div className={styles.rightCol}>
                <TextField
                  type="lastName"
                  name="lastName"
                  value={lastName}
                  placeholder="Last Name"
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('lastName', value )}
                />
              </div> 
            </div>     
            </div>
          </React.Fragment>
       
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
              <h6 className={styles.questionText}> What is the highest level of education have you studied? </h6>
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
                <h6 className={styles.questionText}> What is your experience with solid-state phase transformation?  </h6>
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

              <div className={styles.question}>
                <h6 className={styles.questionText}> What is your experiece with scientific software? </h6>
                <Select
                  type="question3"
                  name="question3"
                  placeholder="---"
                  value= {question4}
                  options={question4Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question4', value )}
                />
              </div>
            </div>
          </div>
          <h6 className={styles.updateError}>{updateError}</h6>
          <div className={styles.editButtons}>
              {!edit ? ( <> <Button onClick={this.handleEdit}> Edit </Button> </>) : ('')} 
              {edit ? (
              <> 
                <Button onClick={this.updateUser}> Save </Button>
                <Button className={styles.cancel}appearance="outline" onClick={this.handleEdit}> Cancel </Button> 
              </>) : ('')} 
          </div>

          <div className={styles.security}>
            <h4 className={styles.header}>Security</h4>
            <h5>Change your password</h5>
            <h6> Click the button below to send a password reset email for this account. </h6> 
            <Button className={styles.resetPassword} length="large" IconComponent={(props) => {return <MailIcon {...props} />}}> RESET YOUR PASSWORD </Button> 
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
  createUserProfileConnect: createUserProfile,
}

export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)

