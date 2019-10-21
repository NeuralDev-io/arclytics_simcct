/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Text area component
 *
 * @version 1.0.0
 * @author Andrew Che
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './TextArea.module.scss'

class TextArea extends Component {
  constructor(props) {
    super(props)
    this.state = {
      err: '',
    }
  }

  handleChange = (e) => {
    const { onChange } = this.props
    onChange(e.target.value)
  }

  render() {
    const {
      placeholder = 'Input',
      isDisabled = false,
      className = '',
      value = '',
      length = 'default',
      cols,
      rows,
      name,
      ...other
    } = this.props
    const { err } = this.state
    const classname = `${styles.textarea} ${length === 'default' ? '' : styles[length]} ${err !== '' && styles.error} ${className || ''}`

    return (
      <div>
        <textarea
          {...other}
          cols={cols}
          rows={rows}
          className={classname}
          placeholder={placeholder}
          name={name}
          value={value}
          onChange={e => this.handleChange(e)}
          disabled={isDisabled}
        />
        <span className="text--sub2">{err}</span>
      </div>
    )
  }
}

TextArea.propTypes = {
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  length: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  placeholder: PropTypes.string,
  isDisabled: PropTypes.bool,
  className: PropTypes.string,
  cols: PropTypes.number,
  rows: PropTypes.number,
}

TextArea.defaultProps = {
  length: 'default',
  placeholder: 'Input',
  isDisabled: false,
  className: '',
  value: '',
  cols: 0,
  rows: 10,
}

export default TextArea
