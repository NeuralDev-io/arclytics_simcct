/**
 * Profile Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import { connect } from 'react-redux'

import TextField from '../../elements/textfield'
import Select from '../../elements/select'
import AppBar from '../../moleisms/appbar'
import Modal from '../../elements/modal'
import Button from '../../elements/button'

import styles from './ProfilePage.module.scss'

class ProfilePage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      email: 'example@example.com',
      firstName: null,
      lastName: null,
      occOptions: [
        { label: 'Student', value: 'student' },
        { label: 'Work', value: 'work' },
      ],
      occupation: { label: 'Student', value: 'student' },
      eduOptions: [
        { label: 'HighSchool', value: 'highSchool' },
        { label: 'University', value: 'university' },
      ],
      education: { label: 'HighSchool', value: 'highSchool' },
      currPassword: null,
      newPassword: null,
      cnfrmPassword: null,
      showDelete: false,
    }
  }

  componentDidMount = () => {
    if (!localStorage.getItem('token')) { this.props.history.push('/signin') }
  }

  handleDeleteModal = () => {
    this.state.showDelete ? this.setState({ showDelete: false }) : this.setState({ showDelete: true })
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  render() {
    const {
      occupation,
      occOptions,
      education,
      eduOptions,
      currPassword,
      newPassword,
      cnfrmPassword,
      showDelete,
      question1,
      question2,
      question3,
      question4,
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
          <div className={styles.profilePicture}> profile picture </div>
          <div className={styles.general}>
            <h4 className={styles.header}>General</h4>
            <div className={styles.row}>
              <h6 className={styles.column}> Email </h6>
              <div className={styles.column}>
                {' '}
                <h6 className={styles.emailText}>
                  {' '}
                  {user.email}
                  {' '}
                </h6>
                {' '}
              </div>
            </div>
            <div className={styles.row}>
              <h6 className={styles.leftCol}>First name</h6>
              <div className={styles.column}>
                <TextField
                  type="firstName"
                  name="firstName"
                  value={user.first_name}
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
                  value={user.last_name}
                  placeholder="Last Name"
                  length="short"
                  onChange={value => this.handleChange('lastName', value)}
                />
              </div>
            </div>
            <div className={styles.row}>
              <div className={styles.column}>
                {' '}
                <h6>Occupation</h6>
                {' '}
              </div>
              <div className={styles.column}>
                <Select
                  type="occupation"
                  name="occupation"
                  placeholder="Choose Occupation"
                  options={occOptions}
                  value={occupation}
                  length="long"
                  onChange={value => this.handleChange('occupation', value)}
                />
              </div>
            </div>
            <div className={styles.row}>
              <div className={styles.column}><h6>Education</h6></div>
              <div className={styles.column}>
                <Select
                  type="occupation"
                  name="occupation"
                  placeholder="Choose Education"
                  options={eduOptions}
                  value={education}
                  length="long"
                  onChange={value => this.handleChange('education', value)}
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
                  value={currPassword}
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
                  value={newPassword}
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
                  value={cnfrmPassword}
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
            <Modal name="deleteModal" show={showDelete} clicked={this.handleDeleteModal}>
            All of your data will be lost. Are you sure you want to delete your account? Please enter your password to confirm
              <TextField
                type="password"
                name="cnfrmDelete"
                placeholder="Enter Password"
                length="long"
              />
              <Button className={styles.cancelDelete} name="cancelDelete" type="button" onClick={this.handleDeleteModal} length="long">
                CANCEL
              </Button>
            </Modal>
          </div>
        </div>
      </React.Fragment>
    )
  }
}

const mapStateToProps = state => ({
  user: state.persist.user,
})

const mapDispatchToProps = {
}

export default connect(mapStateToProps, mapDispatchToProps)(ProfilePage)
