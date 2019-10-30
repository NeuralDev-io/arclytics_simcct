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
  changeThemeRedux,
} from '../../../state/ducks/self/actions'
import TextField from '../../elements/textfield'
import Select from '../../elements/select'
import Button from '../../elements/button'
import LightThemeImg from '../../../assets/theme-images/light.png'
import DarkThemeImg from '../../../assets/theme-images/dark.png'
import { buttonize } from '../../../utils/accessibility'

import styles from './ProfilePage.module.scss'

class ProfilePage extends Component {
  constructor(props) {
    super(props)

    this.state = {
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
      firstName, lastName, aimValue, highestEducationValue, sciTechExpValue, phaseTransformExpValue,
    } = this.state
    const { user, createUserProfileConnect, updateUserProfileConnect } = this.props
    if (!user.profile) {
      if (!(aimValue && highestEducationValue && sciTechExpValue && phaseTransformExpValue)) {
        this.setState({
          updateError: 'Must answer all questions to save',
        })
      } else if (aimValue && highestEducationValue && sciTechExpValue && phaseTransformExpValue) {
        createUserProfileConnect({
          aim: aimValue.value,
          highest_education: highestEducationValue.value,
          sci_tech_exp: sciTechExpValue.value,
          phase_transform_exp: phaseTransformExpValue.value,
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
        aim: aimValue ? aimValue.value : null,
        highest_education: highestEducationValue ? highestEducationValue.value : null,
        sci_tech_exp: sciTechExpValue ? sciTechExpValue.value : null,
        phase_transform_exp: phaseTransformExpValue ? phaseTransformExpValue.value : null,
      })
      this.setState({ edit: false, updateError: null })
    }
  }

  render() {
    const {
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
    const { theme, changeThemeReduxConnect } = this.props

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
        <h3>Theme</h3>
        <div className={styles.themeContainer}>
          <div
            className={`${styles.theme} ${theme === 'light' ? styles.active : ''}`}
            {...buttonize(() => changeThemeReduxConnect('light'))}
          >
            <div className={styles.themeImg}>
              <img src={LightThemeImg} alt="light-theme" />
            </div>
            <h5>Light</h5>
          </div>
          <div
            className={`${styles.theme} ${theme === 'dark' ? styles.active : ''}`}
            {...buttonize(() => changeThemeReduxConnect('dark'))}
          >
            <div className={styles.themeImg}>
              <img src={DarkThemeImg} alt="dark-theme" />
            </div>
            <h5>Dark</h5>
          </div>
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
  theme: PropTypes.string.isRequired,
  changeThemeReduxConnect: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  user: state.self.user,
  theme: state.self.theme,
})

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
  updateUserProfileConnect: updateUserProfile,
  createUserProfileConnect: createUserProfile,
  changeThemeReduxConnect: changeThemeRedux,
}

export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
