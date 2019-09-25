export const constraints = {
  weight: [
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
  ],
  name: [
    {
      check: val => val.trim() !== '',
      message: 'Name is required',
    },
  ],
}

export default constraints
