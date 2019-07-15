import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'
import { ReactComponent as Logo } from '../../../assets/logo_20.svg'
import { login } from '../../../utils/AuthenticationHelper'
import { loginValidation } from '../../../utils/ValidationHelper'

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
        <div className={styles.background}> 
          <div className={styles.form}>
            <div className={styles.logoContainer}>
              <Logo  className={styles.logo} />
              <h3>ARCLYTICS</h3>  
            </div>
            <div className={styles.header}> 
              <h2> Sign in to your account  </h2>
            </div>
            <Formik
              initialValues={{ email: '', password: '' }}
              validate={loginValidation}
              onSubmit={(values, { setSubmitting, setStatus, setErrors }) => {
                setSubmitting(true)
                const promise = new Promise((resolve, reject) => {
                  login(values, resolve, reject)
                })
                promise.then(data => {
                  localStorage.setItem('token', data.token)
                  this.props.history.push('/')
                  setSubmitting(false)
                })
                .catch(err => {
                  console.log(err) // for debug only
                    setErrors({ 
                      email: "Invalid email",
                      password: "Password is invalid"
                    })          
                  setSubmitting(false)
                })
              }}
            >
              {({
                values,
                errors,
                status,
                touched,
                setErrors,
                setStatus,
                handleSubmit,
                setFieldValue,
                isSubmitting
              }) => (
                <form onSubmit={handleSubmit} >
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
                      <h6 className={styles.errors}>{errors.email && touched.email && errors.email}</h6>
                    </div>

                    <div className = {styles.password}> 
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
      </div>
    )
  }
}

const mapStateToProps = state => ({

})

const mapDispatchToProps = {

}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage)

