import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Formik } from 'formik'

class SignupPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
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
              console.log(res.status)
              if (res.status === 201) {
                const promise = new Promise((resolve, reject) => {
                  login({
                    email: values.email,
                    password: values.password
                  }, resolve, reject)
                })
                promise.then(data => {
                  localStorage.setItem("token", data.token)
                  localStorage.setItem("userId", data.user.pk)
                  this.props.getUser(data.user.pk)
                  this.props.history.push('/')
                })
              }
              else if (res.status === 400) {
                setStatus({message: "Email already existed"})
              }
              setSubmitting(false)
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
                
                  <h6>{errors.licence && touched.licence && errors.licence}</h6>
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
  } else if (password.length < 6 || password.length > 20) {
    errors.password = 'Password must be 6-20 characters'
  }
  if (!passwordConfirmed) {
    errors.passwordConfirmed = 'Required'
  } else if (password !== passwordConfirmed) {
    errors.passwordConfirmed = 'Password does not match'
  }

  return errors
}

export const login = async (values, resolve, reject) => {
  fetch('http://localhost:8000/auth/login/', {
    method: 'POST',
    mode: 'cors',
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(values)
  })
  .then(res => {
    if (res.status === 200)
      resolve(res.json())
    else if (res.status === 400)
      reject("Wrong email or password.")
  })
  .catch(err => console.log(err))
}

export const signup = async (values) => {
  const { email, username, password} = values
  const res = await fetch('http://localhost:8000/auth/register/', {
    method: 'POST',
    mode: 'cors',
    headers: {
      "Content-Type": "application/json"
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