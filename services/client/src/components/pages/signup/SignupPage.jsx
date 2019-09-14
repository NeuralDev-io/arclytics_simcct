/**
 * Signup Page
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import AlertCircleIcon from 'react-feather/dist/icons/alert-circle'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { signup } from '../../../api/AuthenticationHelper'
import { signupValidation } from '../../../utils/ValidationHelper'
import { buttonize } from '../../../utils/accessibility'

import Button from '../../elements/button'
import TextField from '../../elements/textfield'
import Modal from '../../elements/modal'

import styles from './SignupPage.module.scss'

class SignupPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showCnfrmModal: false,
    }
  }

  componentDidMount = () => {
    const { history } = this.props
    if (localStorage.getItem('token')) history.push('/')
  }

  render() {
    const { showCnfrmModal } = this.state
    const { history } = this.props
    return (
      <div className={styles.outer}>
        <div className={styles.form}>
          <div className={styles.logoContainer}>
            <Logo className={styles.logo} />
            <h3>ARCLYTICS</h3>
          </div>
          <div className={styles.header}>
            <h3>Sign up</h3>
          </div>
          <Formik
            initialValues={{
              firstName: '',
              lastName: '',
              username: '',
              email: '',
              password: '',
              passwordConfirmed: '',
            }}
            validate={signupValidation}
            onSubmit={async (values, { setSubmitting, setErrors }) => {
              setSubmitting(true)
              const promise = new Promise((resolve, reject) => {
                signup(values, resolve, reject)
              })
              promise.then(() => {
                // If response is successful
                this.setState({
                  showCnfrmModal: true,
                })
                setSubmitting(false)
              })
                .catch((err) => {
                  // If response is unsuccessful
                  if (err === 'This user already exists.') {
                    setErrors({
                      email: 'This email already exists',
                    })
                  } else {
                    setErrors({
                      firstName: 'Invalid first name',
                      lastName: 'Invalid last name',
                      email: 'Invalid email',
                      password: 'Password must contain at least 6 characters',
                      confirmPassword: 'Passwords do not match',
                    })
                  }
                  setSubmitting(false)
                })
            }}
          >
            {({
              values,
              errors,
              touched,
              handleBlur,
              handleSubmit,
              setFieldValue,
              isSubmitting,
            }) => (
              <div>
                <form onSubmit={handleSubmit}>
                <div>
                  <div className={styles.name}>
                    <div className={styles.firstName}>
                      <TextField
                        type="text"
                        name="firstName"
                        onChange={e => setFieldValue('firstName', e)}
                        onBlur={handleBlur}
                        value={values.firstName}
                        placeholder="First Name"
                        length="long"
                        error={errors.firstName && touched.firstName && errors.firstName}
                      />
                    </div>
                    <div className={styles.lastName}>
                      <TextField
                        type="text"
                        name="lastName"
                        onChange={e => setFieldValue('lastName', e)}
                        onBlur={handleBlur}
                        value={values.lastName}
                        placeholder="Last Name"
                        length="long"
                        error={errors.lastName && touched.lastName && errors.lastName}
                      />
                    </div>
                  </div>
                  <div className={styles.emailPassword}>
                    <TextField
                      type="email"
                      name="email"
                      onChange={e => setFieldValue('email', e)}
                      onBlur={handleBlur}
                      value={values.email}
                      placeholder="Email"
                      length="stretch"
                      error={errors.email && touched.email && errors.email}
                    />
                  </div>
                  <div className={styles.emailPassword}>
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
                  <div className={styles.passwordConfirmed}>
                    <TextField
                      type="password"
                      name="passwordConfirmed"
                      length="stretch"
                      value={values.passwordConfirmed}
                      onChange={e => setFieldValue('passwordConfirmed', e)}
                      placeholder="Confirm password"
                      error={
                        errors.passwordConfirmed
                        && touched.passwordConfirmed
                        && errors.passwordConfirmed
                      }
                    />
                  </div>
                  <div className={styles.signUpButton}>
                    <Button
                      name="SIGN UP"
                      appearance="default"
                      type="submit"
                      length="long"
                      disabled={isSubmitting}
                    >
                      SIGN UP
                    </Button>
                  </div>
                </div>
              </form>
                <Modal
                  className={styles.cnfrmModal}
                  // show={showCnfrmModal}
                  show
                >

                  <AlertCircleIcon className={styles.alertCircleIcon} />
                  <h5> Your account has been successfully registered. Verify your account. </h5>
                  <sub>
                    So that you are able to use the full services of the Arclytics Sim application
                    and to be able to personalise your account.
                  </sub>
                  <span>
                    We have sent an email to &nbsp;
                    <span className={styles.email}>
                      arvy.au@gmail.com
                    </span>
                  </span>
                  <h6>Already verified?</h6>
                  <div className={styles.buttons}>
                    <Button
                      appearance="default"
                      className={styles.goToSignIn}
                      onClick={() => history.push('/signin')}
                    >
                      Take me to sign in
                    </Button>
                  </div>
                  <span>
                    Didn&apos;t receive an email? Click&nbsp;
                    <span className={styles.resendEmail} {...buttonize()}>
                      here&nbsp;
                    </span>
                    to resend.
                  </span>
                </Modal>
              </div>
            )}
          </Formik>
          <div>
            <h6>
              Already have an account?&nbsp;
              <Link className={styles.signIn} to="/signin">Sign in</Link>
            </h6>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(SignupPage)
