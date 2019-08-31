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
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { login, forgotPassword } from '../../../utils/AuthenticationHelper'
import { loginValidation, forgotPasswordEmail } from '../../../utils/ValidationHelper'
import { getPersistUserStatus } from '../../../state/ducks/persist/actions'
import TextField from '../../elements/textfield'
import Button from '../../elements/button'

import styles from './LoginPage.module.scss'

/*
  TODO: 
  - once the textfield err prop is fixed uncomment err and need just test edge cases and for Formik move it to the 
  err prop

  - change all the logos too ansto logos
*/

class LoginPage extends Component {
  constructor(props){
    super(props)
    this.state = {
      hasForgotPwd: null,
      forgotEmail: '',
      forgotPwdErr: '',
      emailSent: false,
    }
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

  handleChange = (name, value) => {
    this.setState({
      [name]: value,
    })
  }

  render() {
    const {
      hasForgotPwd,
      forgotEmail,
      emailSent,
      forgotPwdErr,
    } = this.state

    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          <Logo className={styles.logo} />
          <h3> ARCLYTICS </h3>
        </div>
        <div className={`${styles.loginForm} ${!(hasForgotPwd === null)? (hasForgotPwd ? styles.fadeLeftOut : styles.fadeRightIn) : ('')}`}>
          <div className={styles.header}>
            <h3> Sign in to your account  </h3>
          </div>
          <Formik
            initialValues={{ email: '', password: '' }}
            validate={loginValidation}
            onSubmit={(values, { setSubmitting, setErrors }) => {
              setSubmitting(true)
              const promise = new Promise((resolve, reject) => {
                login(values, resolve, reject)
              })
              promise.then((data) => {
                // If response is successful
                localStorage.setItem('token', data.token)
                localStorage.setItem('session', data.session)
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
                        error= {errors.email && touched.email && errors.email}
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
                      onClick={ ()=> this.setState({ hasForgotPwd: true})
                      }>Trouble signing in?</h6>
                    <div className={styles.clear}>
                      <Button
                        className={styles.signIn}
                        name="SIGN IN"
                        type="submit"
                        length="long"
                        isSubmitting={isSubmitting}
                        onClick={handleSubmit}>
                        SIGN IN
                      </Button>
                      <h6>
                        {' '}
                        Don&apos;t have an account?&nbsp;
                        <a className={styles.createAccount} href="http://localhost:3000/signup">
                          Sign up
                        </a>
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
          `${
            styles.forgotPwdForm} ${!(hasForgotPwd === null) ?
            (hasForgotPwd ? styles.fadeLeftIn: styles.fadeRightOut):
            ('')
          }`}>
          <h3 className={styles.header}> Password Reset </h3>
          <span> Enter your email to send a password reset email.</span>
          <TextField
            name="forgotEmail"
            className={styles.forgotEmail}
            type="email"
            placeholder="Enter your email"
            value={forgotEmail}
            onChange={value => this.handleChange('forgotEmail', value)}
            placeholder="Email"
            error={forgotPwdErr}
            length="stretch"
          />    
          <div>
           {/* // TODO: loading takes time make sure button is disabled during loading  */}
           {/* TODO: give space for the span height  */}
           <h6 className={ emailSent ? styles.confirmation : styles.errors}>
            { emailSent ? ('Email has been sent.'): forgotPwdErr}
           </h6>     
            <Button
              className={styles.forgotSubmit}
              type="submit"
              length="long"
              isDisabled={emailSent}
              onClick={()=> {
                const validError = forgotPasswordEmail(forgotEmail)
                if ( validError === ''){
                  const promise = new Promise((resolve, reject) => {
                    forgotPassword(resolve, reject, forgotEmail)
                  })
                  promise.then((data) => {
                    // If response is successful
                    this.setState({
                      forgotPwdErr: '',
                      emailSent: true,
                    })
                  })
                    .catch((err) => {
                      // If response is unsuccessful
                      console.log(err)
                      this.setState({
                        forgotPwdErr: err,
                      })
                    })
                } else {
                  this.setState({
                    forgotPwd: validError
                  })
                }
              }}> Send Email </Button>
            <h6
              className={styles.help}
              onClick={()=> this.setState({ hasForgotPwd: false})}
            >
              Go back to login
            </h6>
          </div>
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
}

const mapDispatchToProps = {
  getUserStatusConnect: getPersistUserStatus,
}

const mapStateToProps = state => ({
  userStatus: state.persist.userStatus,
})

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
