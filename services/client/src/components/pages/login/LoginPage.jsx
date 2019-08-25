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
import { login } from '../../../utils/AuthenticationHelper'
import { loginValidation } from '../../../utils/ValidationHelper'
import { getUserProfile } from '../../../state/ducks/persist/actions'

import TextField from '../../elements/textfield'
import Button from '../../elements/button'

import styles from './LoginPage.module.scss'

class LoginPage extends Component {
  constructor(props){
    super(props)
    this.state = {
      hasForgotPwd: false,
      forgotEmail: '',
    }
  }

  componentDidMount = () => {
    if (localStorage.getItem('token')) this.props.profile ? this.props.history.push('/') : this.props.history.push('/profileQuestions')// eslint-disable-line
  }

  onTextChange = ( name, value) => {
    this.setState({
      [name]: value,
    })
  }

  render() {
    const {hasForgotPwd, forgotEmail } = this.state

    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          <Logo className={styles.logo} />
          <h3> ARCLYTICS </h3>
        </div>
        <div className={`${styles.loginForm} ${hasForgotPwd ? styles.fadeLeftOut : styles.fadeRightIn}`}>
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
                const { getUserProfileConnect, history } = this.props
                getUserProfileConnect()

                // If the user has a profile
                this.props.profile ? history.push('/') : history.push('/profileQuestions')

                setSubmitting(false)
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
                      />
                      <h6 className={styles.errors}>
                        {errors.email && touched.email && errors.email}
                      </h6>
                    </div>

                    <div className={styles.password}>
                      <TextField
                        type="password"
                        name="password"
                        onChange={e => setFieldValue('password', e)}
                        value={values.password}
                        placeholder="Password"
                        length="stretch"
                      />
                      <h6 className={styles.errors}>
                        {errors.password && touched.password && errors.password}
                      </h6>
                    </div>
                    <h6
                      className={styles.help}
                      onClick={ ()=> this.setState({ hasForgotPwd: true})
                      }>Trouble signing in?</h6>
                    <div className={styles.clear}>
                      <Button
                        className={styles.signIn}
                        name="SIGN IN" type="submit"
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
        <div className={`${styles.forgotPwdForm} ${hasForgotPwd ? styles.fadeLeftIn: styles.fadeRightOut}`}>
          {/*TODO: change the messsage when the button is pressed */}
          Enter your email to send a password reset email.
          <TextField
            name="forgotEmail"
            type="email"
            placeholder="Enter your email"
            value={forgotEmail}
            onChange={value => this.onTextChange('forgotEmail', value)}
            placeholder="Email"
            length="stretch"
          />
          <Button > Send Email </Button>
          <h6
            className={styles.help}
            onClick={ ()=> this.setState({ hasForgotPwd: false})
            }>Go back</h6>
        </div>


      </div>
    )
  }
}

LoginPage.propTypes = {
  getUserProfileConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
  profile: PropTypes.shape({
    aim: PropTypes.string,
    highest_education: PropTypes.string,
    sci_tech_exp: PropTypes.string,
    phase_transform_exp: PropTypes.string,
  }),
}

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
}

const mapStateToProps = state => ({
  profile: state.persist.user.profile,

})


export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
