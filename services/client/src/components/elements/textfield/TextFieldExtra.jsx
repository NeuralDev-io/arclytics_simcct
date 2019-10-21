import React from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faExclamationCircle } from '@fortawesome/pro-light-svg-icons/faExclamationCircle'
import Tooltip from '../tooltip'

import styles from './TextFieldExtra.module.scss'

class TextFieldExtra extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      err: '',
    }
  }

  validate = (value) => {
    const { constraints } = this.props
    let err = ''
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

  handleChange = (e) => {
    const { onChange } = this.props
    const err = this.validate(e.target.value)
    if (err !== '') this.setState({ err })
    onChange(e.target.value)
  }

  render() {
    const {
      placeholder = 'Input',
      isDisabled = false,
      type = 'text',
      className = '',
      value = '',
      length = 'default',
      error = '',
      errorTooltipPosition = 'right',
      prefix,
      suffix,
      name,
      ...other
    } = this.props
    const { err } = this.state
    let displayedError = ''
    if (error !== '') {
      displayedError = error
    } else displayedError = err

    const classname = `${styles.input} ${prefix !== '' && styles.withPrefix}`
      + ` ${suffix !== '' && styles.withSuffix} ${displayedError !== '' && styles.error} ${className || ''}`

    return (
      <div className={`${styles.container} ${length === 'default' ? '' : styles[length]}`}>
        {prefix !== '' && <span className={styles.prefix}>{prefix}</span>}
        <input
          {...other}
          type={type}
          className={classname}
          placeholder={placeholder}
          name={name}
          value={value}
          onChange={e => this.handleChange(e)}
          disabled={isDisabled}
        />
        {suffix !== '' && <span className={`${styles.suffix} ${displayedError !== '' && styles.withError}`}>{suffix}</span>}
        {(displayedError !== '') && (
          <Tooltip
            position={errorTooltipPosition}
            className={{ container: styles.errorContainer, tooltip: `${styles.errorTooltip} ${styles[errorTooltipPosition]}` }}
          >
            <FontAwesomeIcon icon={faExclamationCircle} className={styles.icon} size="sm" />
            <span>{displayedError}</span>
          </Tooltip>
        )}
      </div>
    )
  }
}

TextFieldExtra.propTypes = {
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  length: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  type: PropTypes.string,
  placeholder: PropTypes.string,
  isDisabled: PropTypes.bool,
  className: PropTypes.string,
  constraints: PropTypes.arrayOf(PropTypes.shape({
    check: PropTypes.func,
    message: PropTypes.string,
  })),
  error: PropTypes.string,
  errorTooltipPosition: PropTypes.string,
  prefix: PropTypes.string,
  suffix: PropTypes.string,
}

TextFieldExtra.defaultProps = {
  type: 'text',
  length: 'default',
  placeholder: 'Input',
  isDisabled: false,
  className: '',
  value: '',
  constraints: [],
  error: '',
  errorTooltipPosition: 'right',
  prefix: '',
  suffix: '',
}

export default TextFieldExtra
