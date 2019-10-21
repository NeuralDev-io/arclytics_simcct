/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Text field component
 *
 * @version 0.0.0
 * @author Arvy Salazar
 *
 */
export const loginValidation = (values) => {
  const { email, password } = values
  const errors = {}
  if (!email) {
    errors.email = 'Required'
  } else if (
    !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
  ) {
    errors.email = 'Email is invalid'
  }
  if (!password) {
    errors.password = 'Required'
  } else if (password.length < 6 || password.length > 20) {
    errors.password = 'Password is invalid'
  }
  return errors
}

export const signupValidation = (values) => {
  const {
    email, firstName, lastName, password, passwordConfirmed,
  } = values
  const errors = {}

  if (!firstName) {
    errors.firstName = 'Required'
  }
  if (!lastName) {
    errors.lastName = 'Required'
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
    errors.password = 'Password must contain at least 6 characters'
  }

  if (!passwordConfirmed) {
    errors.passwordConfirmed = 'Required'
  } else if (password !== passwordConfirmed) {
    errors.passwordConfirmed = 'Password does not match'
  }

  return errors
}

export const forgotPasswordEmail = (email) => {
  if (!email) return 'Required'
  if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(email)) return 'Invalid email'
  return ''
}

export const passwordResetValidation = (values) => {
  const { newPwd, cnfrmPwd } = values
  const errors = {}

  if (!newPwd) {
    errors.newPwdErr = 'Required'
  } else if (newPwd.length < 6 || newPwd.length > 254) {
    errors.newPwdErr = 'Password is invalid'
  }

  if (!cnfrmPwd) {
    errors.cnfrmPwdErr = 'Required'
  } else if (newPwd !== cnfrmPwd) {
    errors.cnfrmPwdErr = 'Password does not match'
  }
  return errors
}
