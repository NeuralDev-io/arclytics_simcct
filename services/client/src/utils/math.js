/**
 * Round a number to a certain number of decimals
 * @param {number} value
 * @param {number} num number of decimal places
 */
export const roundTo = (value, num) => { // eslint-disable-line
  return Math.round(value * (10 ** num)) / (10 ** num)
}

/**
 * This function takes in an integer and return a string
 * with leading zeros added to satisfy the number of digits specified
 * @param {number} number number to be padded
 * @param {number} n number of digits in the results
 */
export const padZeros = (number, n) => {
  if (number < 10 ** (n - 1)) {
    const len = number >= 0 ? number.toString().length : number.toString().length - 1
    return `${'0'.repeat(n - len)}${number}`
  }
  return number.toString()
}
