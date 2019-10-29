const weightConstraints = [
  {
    check: val => val.trim() !== '',
    message: 'Can\'t be empty',
  },
  {
    check: val => !isNaN(val),
    message: 'Must be a number',
  },
  {
    check: val => parseFloat(val) >= 0,
    message: 'Can\'t be negative',
  },
]

export const constraints = {
  weight: [
    ...weightConstraints,
  ],
  carbon: [
    ...weightConstraints,
    {
      check: val => parseFloat(val) <= 0.8,
      message: 'Carbon can\'t weigh more than 0.8',
    },
  ],
  name: [
    {
      check: val => val.trim() !== '',
      message: 'Name is required',
    },
  ],
}

export default constraints
