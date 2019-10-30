/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Login Page
 *
 * @version 1.0.0
 * @author Arvy Salazar
 *
 * This is the Login Page component that includes the Forget Password and Register
 * page. It also handles the logic required to make API requests for each of these
 * features provided.
 *
 */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { ReactComponent as LogoLight } from '../../../assets/logo_20.svg'
import { ReactComponent as LogoDark } from '../../../assets/logo_20_dark.svg'
import { login, checkAuthStatus } from '../../../api/AuthenticationHelper'
import { loginValidation } from '../../../utils/ValidationHelper'
import ForgotPassword from '../../moleisms/forgot-password'
import TextField from '../../elements/textfield'
import Modal from '../../elements/modal'
import Button from '../../elements/button'
import { buttonize } from '../../../utils/accessibility'
import { addFlashToast } from '../../../state/ducks/toast/actions'

import styles from './LoginPage.module.scss'
import { logError, logInfo } from '../../../api/LoggingHelper'

/*
  TODO:
  - once the textfield err prop is fixed uncomment err and need just test edge cases and for
    Formik move it to the err prop
*/

class LoginPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hasForgotPwd: null,
    }
    this.handleExpiredToken = this.handleExpiredToken.bind(this)
  }

  componentDidMount = () => {
    const { history, location: { state }, addFlashToastConnect } = this.props
    checkAuthStatus().then((res) => {
      if (res.status === 'success') {
        history.push('/')
      }
    })
    if (state && state.accountDeleted) {
      addFlashToastConnect({
        message: 'Account deleted. We hope to see you again',
      }, true)
      return
    }
    if (state && state.forcedOut) {
      addFlashToastConnect({
        message: state.forcedOutMessage,
        options: { variant: 'error' },
      }, true)
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
    const { theme, location: { state }, addFlashToastConnect } = this.props

    let fadeForgot = ('')
    let fadeLogin = ('')
    if (hasForgotPwd !== null) {
      fadeForgot = (hasForgotPwd ? styles.fadeLeftIn : styles.fadeRightOut)
      fadeLogin = (hasForgotPwd ? styles.fadeLeftOut : styles.fadeRightIn)
    }

    return (
      <div className={styles.outer}>
        <div className={styles.logoContainer}>
          {
            theme === 'light'
              ? <LogoLight className={styles.logo} />
              : <LogoDark className={styles.logo} />
          }
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
                login(values, resolve, reject, addFlashToastConnect)
              })
              promise.then(() => {
                // If response is successful
                const { history } = this.props
                // Wait for promise from fetch if the user has a profile
                checkAuthStatus().then((res) => {
                  setSubmitting(true)
                  if (res.status === 'success') {
                    if (!res.isProfile) history.push('/profileQuestions')
                    else if (state && state.forcedOut) history.goBack()
                    else history.push('/')
                  }
                })
              })
                .catch((rejectMsg) => {
                  // If response is unsuccessful
                  setErrors({
                    email: 'Invalid email or password',
                    password: 'Invalid email or password',
                  })
                  setSubmitting(false)
                  logInfo(rejectMsg, 'LoginPage.Formik')
                })
            }}
          >
            {({
              values,
              errors,
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
                        error={errors.email}
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
                        error={errors.password}
                      />
                    </div>
                    <div className={styles.otherLinks}>
                      <h6>
                        {' '}
                        Don&apos;t have an account?&nbsp;
                        <Link className={styles.createAccount} to="/signup">Sign up</Link>
                        {' '}
                      </h6>
                      <a
                        className={styles.help}
                        {...buttonize(() => this.setState({ hasForgotPwd: true }))}
                      >
                        Trouble signing in?
                      </a>
                    </div>
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
                    </div>
                  </div>
                </form>
              </div>
            )}
          </Formik>

          <div className={styles.policy}>
            <p><Link className={styles.links} to="/about/privacy">Privacy policy</Link></p>
            <p><Link className={styles.links} to="/about/disclaimer">Disclaimer</Link></p>
          </div>
        </div>

        <div className={`${styles.forgotPwdForm} ${fadeForgot}`}>
          <ForgotPassword forgotPwdHandler={this.handleForgotPassword} />
        </div>
      </div>
    )
  }
}

LoginPage.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
    goBack: PropTypes.func.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string,
    }),
  }).isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape({
      forcedOut: PropTypes.bool,
      forcedOutMessage: PropTypes.string,
      accountDeleted: PropTypes.bool,
    }),
  }).isRequired,
  theme: PropTypes.string.isRequired,
  addFlashToastConnect: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => ({
  theme: state.self.theme,
})

const mapDispatchToProps = {
  addFlashToastConnect: addFlashToast,
}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)
