import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'

import TextField from '../../elements/textfield'
import Button from '../../elements/button'

import styles from './LoginPage.module.scss'

class LoginPage extends Component {
  componentDidMount = () => {
    if (localStorage.getItem("token"))
    this.props.history.push('/')
  }

  render() {
    return (
      <div className={styles.outer}>
        <div className={styles.form}>
          <div className={styles.logo}>
            {/* TODO: Add Image  */}
            <h2>ARCLYTICS</h2>  
          </div>
          <div className={styles.header}> 
            <h2> Sign in to your account  </h2>
          </div>
           <Formik
            initialValues={{ email: '', password: '' }}
            validate={loginValidation}
            onSubmit={(values, { setSubmitting, setStatus }) => {
              setSubmitting(true)
              const promise = new Promise((resolve, reject) => {
                login(values, resolve, reject)
              })
              promise.then(data => {
                console.log("then block")
                localStorage.setItem('token', data.token)
                this.props.history.push('/')
                setSubmitting(false)
              })
              .catch(err => {
                console.log("error")
                // setStatus({ message: err })
                setSubmitting(false)
              })
            }}
          >
            {({
              values,
              errors,
              status,
              touched,
              handleChange,
              handleBlur,
              handleSubmit,
              setFieldValue,
              isSubmitting
            }) => (
              <form onSubmit={handleSubmit} >
                <div>
                  <TextField
                    type="email"
                    name="email"
                    onChange={e => setFieldValue('email', e)}
                    onBlur={handleBlur}
                    value={values.email}
                    placeholder="Email"
                    length="stretch"
                    className={styles.email}
                  />
                  <h6>{errors.email && touched.email && errors.email}</h6>
                  <TextField
                    type="password"
                    name="password"
                    onChange={e => setFieldValue('password', e)}
                    onBlur={handleBlur}
                    value={values.password}
                    placeholder="Password"
                    length="stretch"
                    className = {styles.password}
                  />
                  {/* TODO: Ask about the error messages and how they should show up*/} 
                  <h6>{errors.password && touched.password && errors.password}</h6>
                  <h6>{status && status.message && status.message}</h6>
                  <div>
                    <a href="http://localhost:3000/signup">  <h6 className={styles.help}>Trouble signing in?</h6> </a>  
                  </div>       
                  <div className={styles.clear}>
                    <Button className={styles.signIn} name="SIGN IN" type="submit" length="long" isSubmitting={isSubmitting}>SIGN IN</Button> 
                    <h6> Don't have an account?  <a className={styles.createAccount} href="http://localhost:3000/signup"> Sign up </a> </h6> 
                  </div>          
                </div>
              </form>
            )}
          </Formik>
        </div> 
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)

export const login = async (values, resolve, reject) => {
  fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    mode: 'cors',
    headers: {
      "content-Type": "application/json"
    },
    body: JSON.stringify(values)
  })
  .then(res => {
    const jsonResponse = res.json() //TODO: for debug only remove later
    console.log(jsonResponse) 
    if (res.status === 200){
      console.log("res status === 200")
      resolve(jsonResponse)
    }
    else if (res.status === 400){
      console.log("res status === 200")
      reject("Wrong email or password.")
    }
  })
  .catch(err => console.log(err))
}

export const loginValidation = values => {
  const { email, password } = values
  let errors = {}
  if (!email) {
    errors.email = 'Required'
  } else if (
    !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
  ) {
    errors.email = 'Invalid email'
  }
  if (!password) {
    errors.password = 'Required'
  } else if (password.length < 6 || password.length > 20) {
    errors.password = 'Password must be 6-20 characters'
  }
  return errors
}