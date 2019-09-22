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
  ms: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be a positive number',
    },
  ],
  bs: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be a positive number',
    },
  ],
  ae: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be a positive number',
    },
  ],
  nucleationStart: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be greater than 0',
    },
  ],
  nucleationFinish: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be a positive number',
    },
    {
      check: val => parseFloat(val) < 100,
      message: 'This value must be less than 100',
    },
  ],
  nucleationParams: [
    {
      check: vals => parseFloat(vals.nucleation_start) <= parseFloat(vals.nucleation_finish),
      message: 'Start temperature can\'t be greater than finish.',
    },
  ],
  startTemp: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be a positive number',
    },
  ],
  cctRate: [
    {
      check: val => val.trim() !== '',
      message: 'This value can\'t be empty',
    },
    {
      check: val => !isNaN(val),
      message: 'This value must be a number',
    },
    {
      check: val => parseFloat(val) > 0,
      message: 'This value must be a positive number',
    },
  ],
}

export default constraints
