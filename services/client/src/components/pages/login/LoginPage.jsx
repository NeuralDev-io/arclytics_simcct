/**
 * Login Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { login } from '../../../api/AuthenticationHelper'
import { loginValidation } from '../../../utils/ValidationHelper'
import { getPersistUserStatus } from '../../../state/ducks/persist/actions'
import ForgotPassword from '../../moleisms/forgot-password'
import TextField from '../../elements/textfield'
import Modal from '../../elements/modal'
import Button from '../../elements/button'
import { buttonize } from '../../../utils/accessibility'

import styles from './LoginPage.module.scss'

/*
  TODO:
  - once the textfield err prop is fixed uncomment err and need just test edge cases and for
    Formik move it to the err prop
  - change all the logos too ansto logos
*/

class LoginPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hasForgotPwd: null,
    }
    this.handleExpiredToken = this.handleExpiredToken.bind(this)
    // this.handler = this.handler.bind(this)
  }

  componentDidMount = () => {
    if (localStorage.getItem('token')) {
      const {
        history,
        getUserStatusConnect,
      } = this.props

      // Check the profile if the user has a token and direct them to write page
      getUserStatusConnect().then(() => {
        const { userStatus } = this.props
        history.push(userStatus.isProfile ? '/' : '/profileQuestions')
      })
    }
  }

  handleExpiredToken = () => {
    const { match } = this.props
    if (match.params.token === 'true') {
      return (
        <Modal shown>
          Your token has expired. Would you like us too resend ?
        </Modal>
      )
    }
    return ('')
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  handleForgotPassword = () => {
  /*
    This method is too update this state from ForgotPassword component.
  */
    this.setState({
      hasForgotPwd: false,
    })
  }

  render() {
    const {
      hasForgotPwd,
    } = this.state

    let fadeForgot = ('')
    let fadeLogin = ('')
    if (hasForgotPwd !== null) {
      fadeForgot = (hasForgotPwd ? styles.fadeLeftIn : styles.fadeRightOut)
      fadeLogin = (hasForgotPwd ? styles.fadeLeftOut : styles.fadeRightIn)
    }

    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          <Logo className={styles.logo} />
          <h3>ARCLYTICS</h3>
        </div>
        {this.handleExpiredToken()}
        <div className={`${styles.loginForm} ${fadeLogin}`}>
          <div className={styles.header}>
            <h3>Sign in to your account</h3>
          </div>
          <Formik
            initialValues={{ email: '', password: '' }}
            validate={loginValidation}
            onSubmit={(values, { setSubmitting, setErrors }) => {
              setSubmitting(true)
              const promise = new Promise((resolve, reject) => {
                login(values, resolve, reject)
              })
              promise.then(() => {
                // If response is successful
                const { history, getUserStatusConnect } = this.props
                // Wait for promise from fetch if the user has a profile
                getUserStatusConnect().then(() => {
                  const { userStatus } = this.props
                  history.push(userStatus.isProfile ? '/' : '/profileQuestions')
                  setSubmitting(true)
                })
              })
                .catch(() => {
                  // If response is unsuccessful
                  setErrors({
                    email: 'Invalid email',
                    password: 'Password is invalid',
                  })
                  setSubmitting(false)
                })
            }}
          >
            {({
              values,
              errors,
              touched,
              handleSubmit,
              setFieldValue,
              isSubmitting,
            }) => (
              <div className={styles.formContainer}>
                <form onSubmit={handleSubmit}>
                  <div>
                    <div className={styles.email}>
                      <TextField
                        type="email"
                        name="email"
                        onChange={e => setFieldValue('email', e)}
                        value={values.email}
                        placeholder="Email"
                        length="stretch"
                        error={errors.email && touched.email && errors.email}
                      />
                    </div>
                    <div className={styles.password}>
                      <TextField
                        type="password"
                        name="password"
                        onChange={e => setFieldValue('password', e)}
                        value={values.password}
                        placeholder="Password"
                        length="stretch"
                        error={errors.password && touched.password && errors.password}
                      />
                    </div>
                    <h6
                      className={styles.help}
                      {...buttonize(() => this.setState({ hasForgotPwd: true }))}
                    >
                      Trouble signing in?
                    </h6>
                    <div className={styles.clear}>
                      <Button
                        className={styles.signIn}
                        name="SIGN IN"
                        type="submit"
                        length="long"
                        isSubmitting={isSubmitting}
                        onClick={handleSubmit}
                      >
                        SIGN IN
                      </Button>
                      <h6>
                        {' '}
                        Don&apos;t have an account?&nbsp;
                        <Link className={styles.createAccount} to="/signup">Sign up</Link>
                        {' '}
                      </h6>
                    </div>
                  </div>
                </form>
              </div>
            )}
          </Formik>
        </div>
        <div
          className={
            `${styles.forgotPwdForm} ${fadeForgot}`
          }
        >
          <ForgotPassword forgotPwdHandler={this.handleForgotPassword} />
        </div>
      </div>
    )
  }
}

LoginPage.propTypes = {
  getUserStatusConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  userStatus: PropTypes.shape({
    isProfile: PropTypes.object,
    verified: PropTypes.bool,
    admin: PropTypes.bool,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string,
    }),
  }).isRequired,
}

const mapDispatchToProps = {
  getUserStatusConnect: getPersistUserStatus,
}

const mapStateToProps = state => ({
  userStatus: state.persist.userStatus,
})

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
