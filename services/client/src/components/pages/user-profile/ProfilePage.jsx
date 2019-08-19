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
} from '../../../state/ducks/users/action'

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
      newPwd: '',
      cnfrmPwd: '',
      pwdOrEmail: false,
      updateError: null,
      edit: false,
    }
  }

  componentDidMount = () => {
    //TODO: Make a user api call here and map it 
    const { history } = this.props
    if (!localStorage.getItem('token')) {
      history.push('/signin') // eslint-disable-line
    }
  }

  handleEdit = () => {
    const { user } = this.props
    const { edit } = this.state
    if (edit) { 
      this.setState({ 
        firstName: user.firsName, // just in case we implement demo mode
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

  render() {
    const {
      firstName,
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
      pwdOrEmail,
      currPwd,
      newPwd,
      cnfrmPwd,
      isCurrPwdCorrect,
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
            <h4 className={styles.header}>Security</h4>
            {
                pwdOrEmail ? (
                  <div>
                    <h6> Change Password </h6>
                    <TextField
                      type="currPwd"
                      name="currPwd"
                      value={currPwd}
                      placeholder="Current Password"
                      length="stretch"
                      onChange={value => this.handleChange('currPwd', value)}
                    />
                    <TextField
                      type="newPwd"
                      name="newPwd"
                      value={newPwd}
                      placeholder="New Password"
                      length="stretch"
                      isDisabled={isCurrPwdCorrect}
                      onChange={value => this.handleChange('newPwd', value)}
                    />
                    <TextField
                      type="cnfrmPwd"
                      name="cnfrmPwd"
                      value={cnfrmPwd}
                      placeholder="Confirm Password"
                      length="stretch"
                      isDisabled={isCurrPwdCorrect}
                      onChange={value => this.handleChange('cnfrmPwd', value)}
                    />
                  </div>
                )
                  : (
                    <div>
                      <h6>Change Email</h6>
                      <TextField
                        type="Change Email"
                        name="Change Email"
                        onChange={value => this.handleChange('cnfrmPwd', value)}
                      />
                    </div>
                  )
            }
            <Button
              className={styles.pwdOrEmail}
              onClick={pwdOrEmail => this.handleChange('pwdOrEmail', !pwdOrEmail)}
              appearance={ pwdOrEmail ? ('default') : ('outline')}
              length="large"
            >
              {pwdOrEmail ? (' Change your Email ?') : ('Change your passsword ?')}
            </Button>
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
  updateUserProfileConnect: PropTypes.func.isRequired,
  createUserProfileConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

const mapStateToProps = state => ({
  user: state.persist.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateUserProfileConnect: updateUserProfile,
  createUserProfileConnect: createUserProfile,
}

export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
