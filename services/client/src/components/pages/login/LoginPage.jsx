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
  componentDidMount = () => {
    if (localStorage.getItem('token')) this.props.history.push('/') // eslint-disable-line
  }

  render() {
    return (
      <div className={styles.outer}>
        <div className={styles.form}>
          <div className={styles.logoContainer}>
            <Logo className={styles.logo} />
            <h3>ARCLYTICS</h3>
          </div>
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
                history.push('/')
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

                    <div>
                      <a href="http://localhost:3000/signup">
                        {' '}
                        <h6 className={styles.help}>Trouble signing in?</h6>
                        {' '}
                      </a>
                    </div>
                    <div className={styles.clear}>
                      <Button className={styles.signIn} name="SIGN IN" type="submit" length="long" isSubmitting={isSubmitting}>
                        SIGN IN
                      </Button>
                      <h6>
                        {' '}
                        Don&apos;t have an account?
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
      </div>
    )
  }
}

LoginPage.propTypes = {
  getUserProfileConnect: PropTypes.func.isRequired,
  history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
}

const mapDispatchToProps = {
  getUserProfileConnect: getUserProfile,
}

export default connect(null, mapDispatchToProps)(LoginPage)
