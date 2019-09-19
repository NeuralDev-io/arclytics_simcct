import validate from 'validate.js'

export const constraints = {
  grainSize: [
    {
      check: val => val.trim() !== '',
      message: 'Grain size can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'Grain size must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'Grain size must be a positive number',
    },
  ],
}

export default constraints
