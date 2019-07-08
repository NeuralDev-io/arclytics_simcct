import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'

import styles from './SignupPagae.module.scss'

class SignupPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      //TODO: do the styles then the designss
      <div>
        <Formik
            initialValues={{ 
              username:'',
              email: '',
              password: '',
              passwordConfirmed: '',
            }}
            validate={signupValidation}
            onSubmit={async (values, { setSubmitting, setStatus }) => {
              setSubmitting(true)
           
              const res = await signup(values)
              if (res.status === 201) {
                //TODO: Store user's auth token
                localStorage.setItem("auth_token", values.auth_token) 
                setStatus({message: values.auth_token})
              }
              else if (res.status === 400) {
                // TODO: read the status message then display appropriate message. Maybe have a special case for unknown messages
                setStatus({message: values.message})
              }
              setSubmitting(false)
            }}
          >
            {({ //TODO: This was copy and pasted 
              values,
              errors,
              status,
              touched,
              handleChange,
              handleBlur,
              handleSubmit,
              isSubmitting
            }) => (
              <form onSubmit={handleSubmit}>
                <div>
                  <div>
                    <div>
                      <input
                        type="text"
                        name="username"
                        onChange={handleChange}
                        onBlur={handleBlur}
                        value={values.username}
                        placeholder="Username"
                      />
                      <h6>{errors.username && touched.username && errors.username}</h6> 
                    </div>
                   
                  </div>
                  <input
                    type="email"
                    name="email"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.email}
                    placeholder="Email"
                  />
                  <h6>{errors.email && touched.email && errors.email}</h6>
                  <input
                    type="password"
                    name="password"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.password}
                    placeholder="Password"
            
                  />
                  <h6>{errors.password && touched.password && errors.password}</h6>
                  <input
                    type="password"
                    name="passwordConfirmed"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.passwordConfirmed}
                    placeholder="Confirm password"
                  />
                  <h6>{status && status.message && status.message}</h6>
                </div>
                <button name="SIGN UP" type="submit" disabled={isSubmitting}>SIGN UP</button>
              </form>
            )}
          </Formik>
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
export const signup = async (values) => {
  const { email, username, password } = values
  const res = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    mode: 'cors',
    headers: {
      "content-Type": "application/json"
    },
    body: JSON.stringify({
      email,
      username,
      password,
    })
  })
  .catch(err => console.log(err))
  return res
}
