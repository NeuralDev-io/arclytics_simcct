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
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { signup } from '../../../utils/AuthenticationHelper'
import { signupValidation } from '../../../utils/ValidationHelper'

import Button from '../../elements/button'
import TextField from '../../elements/textfield'
import styles from './SignupPage.module.scss'

class SignupPage extends Component {
  componentDidMount = () => {
    if (localStorage.getItem('token')) this.props.history.push('/')
  }


  render() {
    return (
      <div className={styles.outer}>
        <div className={styles.form}>
          <div className={styles.logoContainer}>
            <Logo className={styles.logo} />
            <h3> ARCLYTICS </h3>
          </div>
          <div className={styles.signUp}>
            {' '}
            <h3> Sign up </h3>
            {' '}
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
              promise.then((data) => {
                // If response is successful
                localStorage.setItem('token', data.token)
                this.props.history.push('/')
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
                      />
                      <h6 className={styles.errors}>
                        {errors.firstName && touched.firstName && errors.firstName}
                      </h6>

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
                      />
                      <h6 className={styles.errors}>
                        {errors.lastName && touched.lastName && errors.lastName}
                      </h6>
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
                    />
                    <h6 className={styles.errors}>
                      {errors.email && touched.email && errors.email}
                    </h6>
                  </div>

                  <div className={styles.emailPassword}>
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

                  <div className={styles.passwordConfirmed}>
                    <TextField
                      type="password"
                      name="passwordConfirmed"
                      length="stretch"
                      value={values.passwordConfirmed}
                      onChange={e => setFieldValue('passwordConfirmed', e)}
                      placeholder="Confirm password"
                    />
                    <h6 className={styles.errors}>
                      {
                        errors.passwordConfirmed
                        && touched.passwordConfirmed
                        && errors.passwordConfirmed
                      }
                    </h6>
                  </div>
           
                  <div className={styles.signUpButton}>
                    <Button name="SIGN UP" appearance="default" type="submit" length="small" disabled={isSubmitting}> SIGNUP </Button>
                  </div>
                </div>
              </form>
            )}
          </Formik>
          <div>
            <h6>
              {' '}
Already have an account?
              <a href="http://localhost:3000/signin" className={styles.signIn}> Sign in </a>
              {' '}

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
