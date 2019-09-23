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
      updateError: null,
      edit: false,
    }
  }

  componentDidMount = () => {
    const { getUserProfileConnect } = this.props
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
    } = this.state

    return (
      <div className={styles.main}>
        <h3>General</h3>
        <div className={styles.generalFields}>
          <div className={`input-row ${styles.row}`}>
            <span>First name</span>
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
          <div className={`input-row ${styles.row}`}>
            <span> Last name </span>
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

        <h3> About yourself </h3>
        <div className={styles.about}>
          <div className={styles.questions}>
            <div className={styles.question}>
              <span className={styles.questionText}>What sentence best describes you?</span>
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
              <span className={styles.questionText}>
                What is the highest level of education have you studied?
              </span>
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
              <span className={styles.questionText}>
                What is your experience with solid-state phase transformation?
              </span>
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
              <span className={styles.questionText}>
                What is your experience with scientific software?
              </span>
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
              <Button onClick={this.handleEdit} appearance="outline">Edit</Button>
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
      </div>
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
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}


const mapStateToProps = state => ({
  user: state.self.user,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateUserProfileConnect: updateUserProfile,
  createUserProfileConnect: createUserProfile,
}


export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
