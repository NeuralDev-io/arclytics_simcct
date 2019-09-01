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

import AppBar from '../appbar/AppBar'
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
      aimValue: null,
      aimOptions: [
        { label: 'Education', value: 'Education' },
        { label: 'Research', value: 'Research' },
        { label: 'Engineering Work', value: 'Engineering Work' },
        { label: 'Experimentation', value: 'Experimentation' },
      ],
      highestEducationValue: null,
      highestEducationOptions: [
        { label: 'High School', value: 'High School' },
        { label: 'Bachelors Degree', value: 'Bachelors Degree' },
        { label: 'Masters Degree', value: 'Masters Degree' },
        { label: 'PhD', value: 'PhD' },
      ],
      sciTechExpValue: null,
      sciTechOptions: [
        { label: 'Beginner', value: 'Beginner' },
        { label: 'Intermediate', value: 'Intermediate' },
        { label: 'Advanced', value: 'Advanced' },
      ],
      phaseTransformExpValue: null,
      phaseTransformOptions: [
        { label: 'Beginner', value: 'Beginner' },
        { label: 'Intermediate', value: 'Intermediate' },
        { label: 'Advanced', value: 'Advanced' },
      ],
      currentPassword: '',
      currPwdErr: '',
      newPassword: '',
      confirmPassword: '',
      isChangeEmail: false,
      isChangePassword: false,
      editPassword: false,
      updateError: null,
      edit: false,
      editEmail: false,
      newEmail: '',
      emailErr: '',
      isCurrPwdCorrect: false,
    }
  }

  componentDidMount = () => {
    const { history, getUserProfileConnect } = this.props
    if (!localStorage.getItem('token')) history.push('/signin')
    // TODO(arvy@neuraldev.io): This pattern is not ideal either as it turns
    //  an async call to one that is blocking and updates based on returned promise.
    getUserProfileConnect().then(() => {
      const { user } = this.props
      this.setState({
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        aimValue: {
          value: user.profile.aim,
          label: user.profile.aim,
        },
        highestEducationValue: {
          value: user.profile.highest_education,
          label: user.profile.highest_education,
        },
        sciTechExpValue: {
          value: user.profile.sci_tech_exp,
          label: user.profile.sci_tech_exp,
        },
        phaseTransformExpValue: {
          value: user.profile.phase_transform_exp,
          label: user.profile.phase_transform_exp,
        },
      })
    })
  }

  handleEdit = () => {
    const { user } = this.props
    const { edit } = this.state
    if (edit) {
      this.setState({
        firstName: user.first_name,
        lastName: user.last_name,
        aimValue: user.profile
          ? { label: user.profile.aim, value: user.profile.aim }
          : null,
        highestEducationValue: user.profile
          ? { label: user.profile.highest_education, value: user.profile.highest_education }
          : null,
        sciTechExpValue: user.profile
          ? { label: user.profile.sci_tech_exp, value: user.profile.sci_tech_exp }
          : null,
        phaseTransformExpValue: user.profile
          ? { label: user.profile.phase_transform_exp, value: user.profile.phase_transform_exp }
          : null,
        edit: false,
        updateError: null,
      })
    } else {
      this.setState({ edit: true })
    }
  }

  toggleEditButtons = (type) => {
    const { editEmail, editPassword } = this.state
    if (type === 'email') this.setState({ editEmail: !editEmail })
    else if (type === 'password') this.setState({ editPassword: !editPassword })
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
    const { updateEmailConnect } = this.props
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
      currentPassword: value,
    })
    if (value.length >= 6) {
      this.setState({
        isCurrPwdCorrect: true,
      })
    }
  }

  submitNewPassword = () => {
    const { currentPassword, newPassword, confirmPassword } = this.state
    const { changePasswordConnect } = this.props

    changePasswordConnect({
      password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    })
  }

  render() {
    const {
      email,
      firstName,
      lastName,
      aimValue,
      aimOptions,
      highestEducationValue,
      highestEducationOptions,
      sciTechExpValue,
      sciTechOptions,
      phaseTransformExpValue,
      phaseTransformOptions,
      updateError,
      edit,
      currentPassword,
      currPwdErr,
      newPassword,
      confirmPassword,
      isChangeEmail,
      isChangePassword,
      isCurrPwdCorrect,
      newEmail,
      emailErr,
      editPassword,
      editEmail,
    } = this.state

    const { history } = this.props

    return (
      <React.Fragment>
        <AppBar active="profile" redirect={history.push} />

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
                <h6 className={styles.questionText}>What sentence best describes you?</h6>
                <Select
                  type="aim"
                  name="aim"
                  placeholder="---"
                  value={aimValue}
                  options={aimOptions}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('aimValue', value)}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}>
                  What is the highest level of education have you studied?
                </h6>
                <Select
                  type="highestEducation"
                  name="highestEducation"
                  placeholder="---"
                  value={highestEducationValue}
                  options={highestEducationOptions}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('highestEducationValue', value)}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}>
                  What is your experience with solid-state phase transformation?
                </h6>
                <Select
                  type="sciTechExp"
                  name="sciTechExp"
                  placeholder="---"
                  value={sciTechExpValue}
                  options={sciTechOptions}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('sciTechExpValue', value)}
                />
              </div>

              <div className={styles.question}>
                <h6 className={styles.questionText}>
                  What is your experience with scientific software?
                </h6>
                <Select
                  type="phaseTransformExp"
                  name="phaseTransformExp"
                  placeholder="---"
                  value={phaseTransformExpValue}
                  options={phaseTransformOptions}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('phaseTransformExpValue', value)}
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
                  <Button onClick={this.handleEdit} appearance="text">Edit</Button>
                  {' '}
                </>
              )
                : (
                  <>
                    <Button onClick={this.updateUser}>Save</Button>
                    <Button
                      className={styles.cancel}
                      appearance="outline"
                      onClick={this.handleEdit}
                    >
                      Cancel
                    </Button>
                  </>
                )
            }
          </div>

          <div className={styles.security}>
            <h4 className={styles.header}>Security</h4>
            <div className={styles.row}>
              <h5>Change your email</h5>
              <div>
                {
                  !editEmail ? (
                    <>
                      {' '}
                      <Button
                        appearance="text"
                        onClick={() => this.toggleEditButtons('email')}
                      >
                        Change
                      </Button>
                      {' '}
                    </>
                  ) : (
                    <>
                      <Button onClick={() => console.log('Save New Email')}>Save</Button>
                      <Button
                        appearance="outline"
                        onClick={() => this.toggleEditButtons('email')}
                      >
                        Cancel
                      </Button>
                    </>
                  )
                }
              </div>
            </div>
            <div className={styles.row}>
              <h5>Change your password</h5>
              <div>
                <Button
                  appearance="text"
                  onClick={() => this.toggleEditButtons('password')}
                >
                  Update
                </Button>
              </div>
            </div>
          </div>

          <div className={styles.dataAndPersonal}>
            <h4 className={styles.header}> Data and Personalisation </h4>
            <h6>
              Your data, activities and preferences that help make Arclytics Sim service more
              useful for you.
            </h6>
            <Button
              appearance="outline"
              onClick={() => console.log('Review Data Personalisation')}
              className={styles.review}
            >
              Review
            </Button>
          </div>

        </div>
      </React.Fragment>
    )
  }
}

ProfilePage.propTypes = {
  user: PropTypes.shape({
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    email: PropTypes.string,
    profile: PropTypes.shape({
      aim: PropTypes.string,
      highest_education: PropTypes.string,
      sci_tech_exp: PropTypes.string,
      phase_transform_exp: PropTypes.string,
    }),
    admin_profile: PropTypes.shape({
      position: PropTypes.string,
      mobile_number: PropTypes.string,
      verified: PropTypes.bool,
    }),
  }).isRequired,
  getUserProfileConnect: PropTypes.func.isRequired,
  updateUserProfileConnect: PropTypes.func.isRequired,
  createUserProfileConnect: PropTypes.func.isRequired,
  updateEmailConnect: PropTypes.func.isRequired,
  changePasswordConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}


const mapStateToProps = state => ({
  user: state.self.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateUserProfileConnect: updateUserProfile,
  createUserProfileConnect: createUserProfile,
  updateEmailConnect: updateEmail,
  changePasswordConnect: changePassword,
}


export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
