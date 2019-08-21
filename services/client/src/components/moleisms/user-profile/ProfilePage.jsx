/**
 * Profile Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import {
  getUserProfile,
  createUserProfile,
  updateUserProfile,
  updateEmail,
  changePassword,
} from '../../../state/ducks/self/actions'

import TextField from '../../elements/textfield'
import Select from '../../elements/select'
import Button from '../../elements/button'

import styles from './ProfilePage.module.scss'

class ProfilePage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      email: '',
      firstName: '',
      lastName: '',
      question1: '',
      question1Select: [
        { label: 'Q1 Option 1', value: 'Q1 Option 1' },
        { label: 'Q1 Option 2', value: 'Q1 Option 2' },
      ],
      question2: '',
      question2Select: [
        { label: 'Q2 Option 1', value: 'Q2 Option 1' },
        { label: 'Q2 Option 2', value: 'Q2 Option 2' },
      ],
      question3: '',
      question3Select: [
        { label: 'Q3 Option 1', value: 'Q3 Option 1' },
        { label: 'Q3 Option 2', value: 'Q3 Option 2' },
      ],
      question4: '',
      question4Select: [
        { label: 'Q4 Option 1', value: 'Q4 Option 1' },
        { label: 'Q4 Option 2', value: 'Q4 Option 2' },
      ],
      currPwd: '',
      currPwdErr: '',
      newPwd: '',
      newPwdErr: '',
      cnfrmPwd: '',
      cnfrmPwdErr: '',
      pwdOrEmail: true,
      updateError: null,
      edit: false,
      newEmail: '',
      emailErr: '',
      isCurrPwdCorrect: false,
    }
  }

  static getDerivedStateFromProps(props, state) {
    const { user } = props
    const { email, firstName, lastName, question1, question2, question3, question4 } = state
    const initial = {}
    if (props.user.email !== email) {
      initial.email = props.user.email
    }

    if (user.first_name !== firstName && !firstName) {
      initial.firstName = user.first_name
    }

    if (user.last_name !== lastName && !lastName) {
      initial.lastName = user.last_name
    }

    if (user.profile !== null && !(question1 && question2 && question3 && question4)) {
      initial.question1 = { label: user.profile.aim, value: user.profile.aim }
      initial.question2 = { label: user.profile.highest_education, value: user.profile.highest_education }
      initial.question3 = { label: user.profile.sci_tech_exp, value: user.profile.sci_tech_exp }
      initial.question4 = { label: user.profile.phase_transform_exp, value: user.profile.phase_transform_exp }
    }
    return initial
  }

  componentDidMount = () => {
    const { history, getUserProfileConnect, user } = this.props
    if (!localStorage.getItem('token')) {
      history.push('/signin') // eslint-disable-line
    } else {
      getUserProfileConnect()
    }
  }

  handleEdit = () => {
    const { user } = this.props
    const { edit } = this.state
    console.log(user)
    if (edit) { 
      this.setState({ 
        firstName: user.firstName,
        lastName: user.last_name,
        question1: user.profile
          ? { label: user.profile.aim, value: user.profile.aim }
          : null,
        question2: user.profile ? 
          { label: user.profile.highest_education, value: user.profile.highest_education }: 
          null,
        question3: user.profile
          ? { label: user.profile.sci_tech_exp, value: user.profile.sci_tech_exp }
          : null,
        question4: user.profile ? 
          { label: user.profile.phase_transform_exp, value: user.profile.phase_transform_exp }: 
          null,
        edit: false,
        updateError: null,
      })
    } else {
      this.setState({ edit: true })
    }
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  updateUser = () => {
    const {
      firstName, lastName, question1, question2, question3, question4,
    } = this.state
    const { user, createUserProfileConnect, updateUserProfileConnect } = this.props

    if (!user.profile) {
      if (!(question1 && question2 && question3 && question4)) {
        this.setState({
          updateError: 'Must answer all questions to save',
        })
      } else if (question1 && question2 && question3 && question4) {
        createUserProfileConnect({
          aim: question1.value,
          highest_education: question2.value,
          sci_tech_exp: question3.value,
          phase_transform_exp: question4.value,
        })
        updateUserProfileConnect({
          first_name: firstName,
          last_name: lastName,
        })
        this.setState({ edit: false, updateError: null })
      }
    } else if (user.profile) {
      updateUserProfileConnect({
        first_name: firstName,
        last_name: lastName,
        aim: question1 ? question1.value : null,
        highest_education: question2 ? question2.value : null,
        sci_tech_exp: question2 ? question3.value : null,
        phase_transform_exp: question3 ? question4.value : null,
      })
      this.setState({ edit: false, updateError: null })
    }
  }

  handleUpdateEmail = (value) => {
    const { updateEmailConnect, } = this.props
    if (!value) {
      this.setState({
        emailErr: 'Required',
      })
    } else if (
      !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(value)
    ) {
      this.setState({
        emailErr: 'Invalid email',
      })
    } else {
      console.log(value)
      updateEmailConnect({ new_email: value })
    }
  }

  handleChangeCurrPwd = (value) => {
    this.setState({
      currPwd: value,
    })
    if (value.length >= 6) {
      this.setState({
        isCurrPwdCorrect: true,
      })
    }
  }

  submitNewPassword = (value) => {
    const { currPwd, newPwd, cnfrmPwd } = this.state
    const { changePasswordConnect } = this.props

    changePasswordConnect({
      password: currPwd,
      new_password: newPwd,
      confirm_password: cnfrmPwd,
    })
  }

  render() {
    const {
      email,
      firstName,
      lastName,
      question1, question1Select,
      question2, question2Select,
      question3, question3Select,
      question4, question4Select,
      updateError,
      edit,
      pwdOrEmail,
      currPwd,
      currPwdErr,
      newPwd,
      cnfrmPwd,
      isCurrPwdCorrect,
      newEmail,
      emailErr,
    } = this.state
    const { user } = this.props
    return (
      <React.Fragment>
        <div className={styles.main}>
          <h4 className={styles.header}>General</h4>
          <div className={styles.generalFields}>
            <div className={styles.row}>
              <h6 className={styles.leftCol}> Email </h6>
              <div className={styles.rightCol}>
                <h6>
                  {email}
                </h6>
              </div>
            </div>
            <div className={styles.row}>
              <h6 className={styles.leftCol}>First name</h6>
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
                  onChange={value => this.handleChange('lastName', value)}
                />
              </div>
            </div>
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
                  value={question1}
                  options={question1Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question1', value)}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}>
                  What is the highest level of education have you studied?
                </h6>
                <Select
                  type="question2"
                  name="question2"
                  placeholder="---"
                  value={question2}
                  options={question2Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question2', value)}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}>
                  What is your experience with solid-state phase transformation?
                </h6>
                <Select
                  type="question2"
                  name="question2"
                  placeholder="---"
                  value={question3}
                  options={question3Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question3', value)}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}>
                  What is your experiece with scientific software?
                </h6>
                <Select
                  type="question3"
                  name="question3"
                  placeholder="---"
                  value={question4}
                  options={question4Select}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question4', value)}
                />
              </div>
            </div>
          </div>
          <h6 className={styles.updateError}>{updateError}</h6>
          <div className={styles.editButtons}>
            { 
              !edit ? (
                <>
                  {' '}
                  <Button onClick={this.handleEdit}> Edit </Button>
                  {' '}
                </>
              )
                : (
                  <>
                    <Button onClick={this.updateUser}> Save </Button>
                    <Button className={styles.cancel} appearance="outline" onClick={this.handleEdit}> Cancel </Button>
                  </>
                )
            }
            
          </div>

          <div className={styles.security}>
            <div className={styles.header}>
              <h4> Security </h4>
              <Button
                className={styles.pwdOrEmail}
                onClick={() => this.handleChange('pwdOrEmail', !pwdOrEmail)}
                appearance="outline"
                length="large"
              >
                {pwdOrEmail ? (' Change your email') : ('Change or reset passsword')}
              </Button>
            </div>
            
            {
                pwdOrEmail ? (
                  <div className={styles.changePassword}>
                    <h5> Change Password </h5>
                    <h6> Password must be 6 letters long </h6>
                    <div className={styles.row}>
                      <h6 className={styles.lCol}> Current Password </h6>
                      <div className={styles.rCol}>
                        <TextField
                          type="password"
                          name="currPwd"
                          value={currPwd}
                          placeholder="Current Password"
                          length="stretch"
                          onChange={value => this.handleChangeCurrPwd(value)}
                          err={currPwdErr}
                        />
                      </div>
                    </div>

                    <div className={styles.row}>
                      <h6 className={styles.lCol}> New Password </h6>
                      <div className={styles.rCol}>
                        <TextField
                          type="password"
                          name="newPwd"
                          value={newPwd}
                          placeholder="New Password"
                          length="stretch"
                          isDisabled={!isCurrPwdCorrect}
                          onChange={value => this.handleChange('newPwd', value)}
                        />
                      </div>
                    </div>

                    <div className={styles.row}>
                      <h6 className={styles.lCol}> Confirm Password </h6>
                      <div className={styles.rCol}>
                        <TextField
                          type="password"
                          name="cnfrmPwd"
                          value={cnfrmPwd}
                          placeholder="Confirm Password"
                          length="stretch"
                          isDisabled={!isCurrPwdCorrect}
                          onChange={value => this.handleChange('cnfrmPwd', value)}
                        />
                      </div>
                    </div>
                    <Button className={styles.submitPwd} onClick={() => this.submitNewPassword()}>
                      Change Password
                    </Button>
                  </div>
                )
                  : (
                    <div className={styles.changeEmail}>
                      <h5>Change Email</h5>
                      <h6>A request to change your email will be sent to the specified email address in the textfield below </h6>
                      <div className={styles.row}>
                        <div className={styles.lCol}>
                          <h6>Email</h6>
                        </div>
                        <div className={styles.rCol}>
                          <TextField
                            type="Change Email"
                            name="Change Email"
                            value={newEmail}
                            length="stretch"
                            onChange={value => this.handleChange('newEmail', value)}
                            err={emailErr}
                          />
                        </div>
                      </div>
                      <Button className={styles.submitEmail} onClick={() => this.handleUpdateEmail(newEmail)}>
                        Verify new email
                      </Button>

                    </div>
                  )
            }
          </div>
          <div className={styles.dataAndPersonal}>
            <h4 className={styles.header}> Data and Personalisation </h4>
            <h6>
              Your data, activities and preferences that help make Arclytics Sim service more
              useful for you.
            </h6>

            <Button> Review </Button>
          </div>

        </div>
      </React.Fragment>
    )
  }
}

ProfilePage.propTypes = {
  user: PropTypes.arrayOf(PropTypes.shape({
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    email: PropTypes.string,
    profile: PropTypes.shape({
      aim: PropTypes.string,
      highest_education: PropTypes.string,
      sci_tech_exp: PropTypes.string,
      phase_transform_exp: PropTypes.string,
    }),
  })).isRequired,
  getUserProfileConnect: PropTypes.func.isRequired,
  updateUserProfileConnect: PropTypes.func.isRequired,
  createUserProfileConnect: PropTypes.func.isRequired,
  updateEmailConnect: PropTypes.func.isRequired,
  changePasswordConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}


const mapStateToProps = state => ({
  user: state.user.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateUserProfileConnect: updateUserProfile,
  createUserProfileConnect: createUserProfile,
  updateEmailConnect: updateEmail,
  changePasswordConnect: changePassword,
}


export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
