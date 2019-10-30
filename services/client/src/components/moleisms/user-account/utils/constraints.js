export const constraints = {
  email: [
    {
      check: val => val.trim() !== '',
      message: 'Email can\'t be empty',
    },
    {
      check: val => /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(val),
      message: 'Invalid email',
    },
  ],
  password: [
    {
      check: val => val !== '',
      message: 'Password can\'t be empty',
    },
    {
      check: val => val.length >= 6 && val.length <= 24,
      message: 'Password must be 6-24 characters',
    },
  ],
  passwordMatch: [
    {
      check: vals => vals.password === vals.passwordConfirm,
      message: 'Password does not match.',
    },
  ],
}

export default constraints
