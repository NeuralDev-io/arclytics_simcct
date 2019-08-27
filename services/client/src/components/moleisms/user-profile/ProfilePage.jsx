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
      aim: '',
      aimOptions: [
        { label: 'Education', value: 'Education' },
        { label: 'Research', value: 'Research' },
        { label: 'Engineering Work', value: 'Engineering Work' },
        { label: 'Experimentation', value: 'Experimentation' },
      ],
      highestEducation: '',
      highestEducationOptions: [
        { label: 'High School', value: 'High School' },
        { label: 'Bachelors Degree', value: 'Bachelors Degree' },
        { label: 'Masters Degree', value: 'Masters Degree' },
        { label: 'PhD', value: 'PhD' },
      ],
      sciTechExp: '',
      sciTechOptions: [
        { label: 'Beginner', value: 'Beginner' },
        { label: 'Intermediate', value: 'Intermediate' },
        { label: 'Advanced', value: 'Advanced' },
      ],
      phaseTransformExp: '',
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
      updateError: null,
      edit: false,
      newEmail: '',
      emailErr: '',
      isCurrPwdCorrect: false,
    }
  }

  componentDidMount = () => {
    const { history, getUserProfileConnect } = this.props
    if (!localStorage.getItem('token')) history.push('/signin')
    getUserProfileConnect().then(() => {
      const { user } = this.props
      if (user.profile !== undefined) {
        this.setState({
          aim: {
            label: user.profile.aim,
            value: user.profile.aim,
          },
          highestEducation: {
            label: user.profile.highest_education,
            value: user.profile.highest_education,
          },
          sciTechExp: {
            label: user.profile.sci_tech_exp,
            value: user.profile.sci_tech_exp,
          },
          phaseTransformExp: {
            label: user.profile.phase_transform_exp,
            value: user.profile.phase_transform_exp,
          },
        })
      }
    })
  }

  handleEdit = () => {
    const { user } = this.props
    const { edit } = this.state
    console.log(user)
    if (edit) {
      this.setState({
        firstName: user.first_name,
        lastName: user.last_name,
        aim: user.profile
          ? { label: user.profile.aim, value: user.profile.aim }
          : null,
        highestEducation: user.profile
          ? { label: user.profile.highest_education, value: user.profile.highest_education }
          : null,
        sciTechExp: user.profile
          ? { label: user.profile.sci_tech_exp, value: user.profile.sci_tech_exp }
          : null,
        phaseTransformExp: user.profile
          ? { label: user.profile.phase_transform_exp, value: user.profile.phase_transform_exp }
          : null,
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
      aim,
      aimOptions,
      highestEducation,
      highestEducationOptions,
      sciTechExp,
      sciTechOptions,
      phaseTransformExp,
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
    } = this.state

    const { history, user } = this.props

    /* const { user } = this.props
    if (user.profile !== undefined) {
      this.setState({
        aim: {
          label: user.profile.aim,
          value: user.profile.aim,
        },
        highestEducation: {
          label: user.profile.highest_education,
          value: user.profile.highest_education,
        },
        sciTechExp: {
          label: user.profile.sci_tech_exp,
          value: user.profile.sci_tech_exp,
        },
        phaseTransformExp: {
          label: user.profile.phase_transform_exp,
          value: user.profile.phase_transform_exp,
        },
      })
    } */

    return (
      <React.Fragment>
        <AppBar active="admin" redirect={history.push} />

        <div className={styles.main}>
          <h4 className={styles.header}>General</h4>
          <div className={styles.generalFields}>
            <div className={styles.row}>
              <h6 className={styles.leftCol}> Email </h6>
              <div className={styles.rightCol}>
                <h6>
                  {user.email}
                </h6>
              </div>
            </div>
            <div className={styles.row}>
              <h6 className={styles.leftCol}>First name</h6>
              <div className={styles.rightCol}>
                <TextField
                  type="firstName"
                  name="firstName"
                  value={user.first_name}
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
                  value={user.last_name}
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
                  type="aim"
                  name="aim"
                  placeholder="---"
                  value={aim}
                  options={aimOptions}
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
                  type="highestEducation"
                  name="highestEducation"
                  placeholder="---"
                  value={highestEducation}
                  options={highestEducationOptions}
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
                  type="sciTechExp"
                  name="sciTechExp"
                  placeholder="---"
                  value={sciTechExp}
                  options={sciTechOptions}
                  length="stretch"
                  isDisabled={!edit}
                  onChange={value => this.handleChange('question3', value)}
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
                  value={phaseTransformExp}
                  options={phaseTransformOptions}
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
              <div>
                <h6>Email</h6>
                <Button
                  onClick={() => console.log('Change Email')}
                >
                  Change email
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
