/**
 * Function to validate a value against an array of constraints
 * @param {string} value value string
 * @param {array} constraints array of constraint objects
 * @returns {string} err: undefined if value is valid, otherwise an
 * error string
 */
export const validate = (value, constraints) => {
  let err
  const BreakException = {}
  try {
    constraints.forEach((constraint) => {
      if (!constraint.check(value)) {
        err = constraint.message
        throw BreakException
      }
    })
  } catch (ex) {
    if (ex !== BreakException) throw ex
  }
  return err
}

export const validateGroup = (values, constraints) => {
  let err
  const BreakException = {}
  try {
    constraints.forEach((constraint) => {
      if (!constraint.check(values)) {
        err = constraint.message
        throw BreakException
      }
    })
  } catch (ex) {
    if (ex !== BreakException) throw ex
  }
  return err
}
