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

import Button from '../../elements/button'
// import TextField from '../../elements/textfield/TextField';
import TextField from '../../elements/textfield'

import styles from './SignupPage.module.scss'

class SignupPage extends Component {
  
  // constructor(props) {
  //   super(props)
  //   this.state = {
  //     value: undefined,
  //   }
  // }

  componentDidMount = () => {

  }

  // handleChange = (val) => {
  //   this.setState({
  //     value: val,
  //   })
  // }

  render() {
    return (
      //TODO: do the styles then the designss
      <div className={styles.outer}>
        <div className={styles.form}>
          <div className={styles.logo}> <h3> ARCLYTICS </h3> </div>
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
                  localStorage.setItem("auth_token", data.auth_token)
                  setSubmitting(false)
                })
                .catch(err => {
                  setStatus({ message: err })
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
                    {/* //FIXME: need to add wrapping divs around matching inputs and headings */}
                    <div className={styles.name}>             
                      <TextField
                        type="text"
                        name="firstName"
                        onChange={e => setFieldValue('firstName', e)}
                        onBlur={handleBlur}
                        value={values.firstName}
                        placeholder="First Name"
                        length="long"
                        className={styles.firstName}
                      />
                      <h6>{errors.firstName && touched.firstName && errors.firstName}</h6> 
                      
                      <TextField
                        type="text"
                        name="lastName"
                        onChange={e => setFieldValue('lastName', e)}
                        onBlur={handleBlur}
                        value={values.lastName}
                        placeholder="Last Name"
                        length="long"
                        className={styles.lastName}
                      />
                      <h6>{errors.lastName && touched.lastName && errors.lastName}</h6> 
                    </div>
                    <TextField
                      type="text"
                      name="username"
                      onChange={e => setFieldValue('username', e)}
                      onBlur={handleBlur}
                      value={values.username}
                      placeholder="Username"
                      length="stretch"
                      className = {styles.emailPassword}
                    />
                    <h6>{errors.username && touched.username && errors.username}</h6> 

                    <TextField
                      type="email"
                      name="email"
                      onChange={e => setFieldValue('email', e)}
                      onBlur={handleBlur}
                      value={values.email}
                      placeholder="Email"
                      length="stretch"
                      className = {styles.emailPassword}
                    />
                    <h6>{errors.email && touched.email && errors.email}</h6>

                    <TextField
                      type="password"
                      name="password"
                      onChange={e => setFieldValue('password', e)}
                      value={values.password}
                      placeholder="Password"
                      length="stretch"
                      className = {styles.emailPassword}
                    />
                    <h6>{errors.password && touched.password && errors.password}</h6>
                  
                    <TextField
                      type="password" 
                      name="passwordConfirmed"
                      length="stretch"
                      value={values.passwordConfirmed}
                      onChange={e => setFieldValue('passwordConfirmed', e)}
                      placeholder="Confirm password"
                      className = {styles.passwordConfirmed}
                    />
                    <h6>{status && status.message && status.message}</h6>

                  </div>
                  <div className={styles.signUpButton}>
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


//TODO: Move this function for Validation and import it. Talk to matt 
export const signupValidation = values => {
  //TODO: Add validation to first name and last name 
  const {
    email, username, password, passwordConfirmed
  } = values
  let errors = {}

  if (!username) {
    errors.username = 'Required'
  }
  
  if (!email) {
    errors.email = 'Required'
  } else if (
    !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
  ) {
    errors.email = 'Invalid email'
  }

  if (!password) {
    errors.password = 'Required'
  } else if (password.length < 6 || password.length > 254) {
    errors.password = 'Password must be'
  }
  if (!passwordConfirmed) {
    errors.passwordConfirmed = 'Required'
  } else if (password !== passwordConfirmed) {
    errors.passwordConfirmed = 'Password does not match'
  }

  return errors
}


//TODO: Move this function to a separate file for Authentication and import it. Talk to Matt
export const signup = async (values, resolve, reject) => {
  const { email, username, password, firstName, lastName } = values
  fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    mode: 'cors',
    headers: {
      "content-Type": "application/json"
    },
    body: JSON.stringify({
      email,
      username,
      password,
      first_name: firstName,
      last_name: lastName
    })
  })
  .then(res => {
    const jsonResponse = res.json() //TODO: for debug only remove later
    console.log(jsonResponse) 
    if (res.status === 200)
      resolve(res.json())
    else if (res.status === 400)
      reject("Error")
  })
  .catch(err => console.log(err))
}
