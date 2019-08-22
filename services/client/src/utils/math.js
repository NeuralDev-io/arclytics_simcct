/**
 * Round a number to a certain number of decimals
 * @param {number} value
 * @param {number} num number of decimal places
 */
export const roundTo = (value, num) => { // eslint-disable-line
  return Math.round(value * (10 ** num)) / (10 ** num)
}
