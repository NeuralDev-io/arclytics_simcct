import React, { Component } from 'react'
import { connect } from 'react-redux'

class SignupPage extends Component {
  componentDidMount = () => {

  }

  render() {
    return (
      <div>
         <Formik
            initialValues={{ email: '', password: '' }}
            validate={loginValidation}
            onSubmit={(values, { setSubmitting, setStatus }) => {
              setSubmitting(true)
              const promise = new Promise((resolve, reject) => {
                login(values, resolve, reject)
              })
              promise.then(data => {
                localStorage.setItem("token", data.token)
                localStorage.setItem("userId", data.user.pk)
                this.props.getUser(data.user.pk)
                this.props.history.push('/')
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
              handleChange,
              handleBlur,
              handleSubmit,
              isSubmitting
            }) => (
              <form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.input}>
                  <input
                    type="email"
                    name="email"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.email}
                    placeholder="Email"
                    className={styles.textField}
                  />
                  <h6 className={styles.errors}>{errors.email && touched.email && errors.email}</h6>
                  <input
                    type="password"
                    name="password"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.password}
                    placeholder="Password"
                    className={styles.textField}
                  />
                  <h6 className={styles.errors}>{errors.password && touched.password && errors.password}</h6>
                  <h6 className={styles.errors}>{status && status.message && status.message}</h6>
                </div>
                <ButtonLong name="SIGN IN" type="submit" isSubmitting={isSubmitting} className={styles.button} />
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
