import { padZeros } from './math'

/**
 * This function takes a date string and convert it to a more human readable format.
 * It doesn't check if the date string is valid and will return empty string
 * if any error happens.
 * @param {string} datestring a string that will be parse to create date
 */
// eslint-disable-next-line
export function dangerouslyGetDateTimeString(datestring) {
  try {
    const date = new Date(datestring)
    return `${padZeros(date.getDate(), 2)}-${padZeros(date.getMonth() + 1, 2)}-${date.getFullYear()}
    ${padZeros(date.getHours(), 2)}:${padZeros(date.getMinutes(), 2)}:${padZeros(date.getSeconds(), 2)}`
  } catch (err) {
    return ''
  }
}
