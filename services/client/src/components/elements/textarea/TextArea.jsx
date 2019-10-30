/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Text area component
 *
 * @version 1.1.0
 * @author Andrew Che, Dalton Le
 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './TextArea.module.scss'

class TextArea extends Component {
  constructor(props) {
    super(props)
    this.state = {
      highlightMax: false,
    }
  }

  handleChange = (e) => {
    const { onChange, maxCharacters } = this.props
    const val = e.target.value
    if (maxCharacters > -1) {
      // check length of new value
      if (val.length > maxCharacters) {
        this.setState({ highlightMax: true })
        setTimeout(() => {
          this.setState({ highlightMax: false })
        }, 500)
        return
      }
    }
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
      maxCharacters,
      ...other
    } = this.props
    const { highlightMax } = this.state
    const classname = `${styles.textarea}
      ${length === 'default' ? '' : styles[length]}
      ${highlightMax ? styles.errored : ''}
      ${className || ''}`

    return (
      <div className={styles.container}>
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
        {
          maxCharacters > -1
            ? (
              <span className={`${styles.error} text--sub2 ${highlightMax ? styles.active : ''}`}>
                {value.length}
                /
                {maxCharacters}
              </span>
            )
            : ''
        }
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
  maxCharacters: PropTypes.number,
}

TextArea.defaultProps = {
  length: 'default',
  placeholder: 'Input',
  isDisabled: false,
  className: '',
  value: '',
  cols: 0,
  rows: 10,
  maxCharacters: -1,
}

export default TextArea
