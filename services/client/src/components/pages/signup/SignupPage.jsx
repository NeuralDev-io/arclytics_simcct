/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Text field component
 *
 * @version 0.0.0
 * @author Arvy Salazar
 * @github Xaraox
 */
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import { signup } from '../../../utils/AuthenticationHelper'
import { signupValidation } from '../../../utils/ValidationHelper'

import Button from '../../elements/button'
import TextField from '../../elements/textfield'
import styles from './SignupPage.module.scss'

class SignupPage extends Component {

  componentDidMount = () => {
    if (localStorage.getItem("token"))
      this.props.history.push('/')
  }


  render() {
    return (
      <div className={styles.outer}>
        <div className={styles.form}>
          <div className={styles.logo}><h3> ARCLYTICS </h3> </div>
          <div className={styles.signUp}> <h3> Sign Up </h3> </div>
          <Formik
              initialValues={{ 
                firstName:'',
                lastName:'',
                username:'',
                email: '',
                password: '',
                passwordConfirmed: '',
              }}
              validate={signupValidation}
              onSubmit={async (values, { setSubmitting, setStatus }) => {
                setSubmitting(true)
                const promise = new Promise((resolve, reject) => {
                  signup(values, resolve, reject)
                })
                promise.then(data => {
                  localStorage.setItem('token', data.token)
                  this.props.history.push('/')
                  setSubmitting(false)
                })
                .catch(err => {
                  setStatus({ message: err})
                  setSubmitting(false)
                })
              }}
            >
              {({
                values,
                errors,
                status,
                touched,
                handleBlur,
                handleSubmit,
                setFieldValue,
                isSubmitting,
                submitForm
              }) => (
                <form onSubmit={handleSubmit}>
                  <div>
                    <div className={styles.name}>
                      <div  className={styles.firstName} >
                        <TextField
                          type="text"
                          name="firstName"
                          onChange={e => setFieldValue('firstName', e)}
                          onBlur={handleBlur}
                          value={values.firstName}
                          placeholder="First Name"
                          length="long"
                         
                        />
                        <h6 className={styles.errors}>{errors.firstName && touched.firstName && errors.firstName}</h6>             
                  
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
                        <h6 className={styles.errors}>{errors.lastName && touched.lastName && errors.lastName}</h6> 
                      </div> 
                 
                    </div>
                    <div className = {styles.emailPassword}>
                      <TextField
                        type="email"
                        name="email"
                        onChange={e => setFieldValue('email', e)}
                        onBlur={handleBlur}
                        value={values.email}
                        placeholder="Email"
                        length="stretch"
                      />
                      <h6 className={styles.errors}>{errors.email && touched.email && errors.email}</h6>
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
                      <h6 className={styles.errors}>{errors.password && touched.password && errors.password}</h6>
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
                        <h6 className={styles.errors}>{errors.passwordConfirmed && touched.passwordConfirmed && errors.passwordConfirmed}</h6>
                    </div> 
                  </div>
                  <div className={styles.signUpButton}>
                    <h6 className={styles.errors}>{status && status.message && status.message}</h6>
                    <Button name="SIGN UP" appearance="default" type="submit" length="small" disabled={isSubmitting}> SIGNUP </Button>
                  </div>
                </form>
              )}
            </Formik>
          <div>
            <h6> Already have an account? <a href="localhost:signin" className={styles.signIn}> Sign in </a> </h6>
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



