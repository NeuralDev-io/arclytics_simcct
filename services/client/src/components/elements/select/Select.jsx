/**
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * Select button component. A wrapper around react-select component.
 * https://github.com/JedWatson/react-select
 *
 * @version 1.0.0
 * @author Dalton Le
 */

import React from 'react'
import PropTypes from 'prop-types'
import ReactSelect from 'react-select'

import styles from './Select.module.scss'
import { getColor } from '../../../utils/theming'

// TODO: include validation
const Select = (props) => {
  const {
    length,
    isDisabled = false,
    placeholder = '',
    name,
    className,
    options,
    defaultValue,
    value,
    onChange,
    ...other
  } = props
  const classname = `${styles.select} ${length === 'default' ? '' : styles[length]} ${className || ''}`

  const customStyles = {
    container: provided => ({
      ...provided,
      width: (() => {
        if (length === 'short') return '7rem'
        if (length === 'long') return '10rem'
        if (length === 'stretch') return '100%'
        return '7.5rem'
      })(),
    }),
    control: (provided, state) => ({
      ...provided,
      backgroundColor: getColor('--n10'),
      borderRadius: 6,
      borderColor: getColor('--n10'),
      borderWidth: 1,
      padding: '0 .25rem 0 .55rem',
      height: '2.25rem',
      minHeight: 'initial',
      cursor: state.isDisabled ? 'not-allowed' : 'pointer',

      '&:hover': {
        backgroundColor: getColor('--n20'),
        borderColor: getColor('--n20'),
      },
    }),
    valueContainer: () => ({
      padding: 0,
    }),
    dropdownIndicator: provided => ({
      ...provided,
      height: '1.25rem',
      padding: '0 .5rem',
    }),
    clearIndicator: provided => ({
      ...provided,
      height: '1.25rem',
      padding: '0 .5rem',
    }),
    singleValue: (provided, state) => ({
      ...provided,
      color: (() => {
        if (state.isDisabled) return getColor('--n300')
        if (state.hasValue) return getColor('--n900')
        return getColor('--n600')
      })(),
    }),
    option: provided => ({
      ...provided,
      padding: '.5rem .75rem',
    }),
    placeholder: (provided, state) => ({
      ...provided,
      color: state.isDisabled ? getColor('--n300') : getColor('--n600'),
    }),
  }

  return (
    <ReactSelect
      className={classname}
      name={name}
      placeholder={placeholder}
      options={options}
      defaultValue={defaultValue}
      value={value}
      onChange={onChange}
      styles={customStyles}
      isDisabled={isDisabled}
      isSearchable={false}
      theme={theme => ({
        ...theme,
        colors: {
          ...theme.colors,
          primary: getColor('--arc500'),
          primary25: getColor('--arc50'),
        },
      })}
      {...other}
    />
  )
}

Select.propTypes = {
  className: PropTypes.string,
  name: PropTypes.string.isRequired,
  /* length?: "default" | "short" | "long" | "stretch" */
  length: PropTypes.string,
  isDisabled: PropTypes.bool,
  placeholder: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string,
  })),
  defaultValue: PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string,
  }),
  value: PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string,
  }),
  onChange: PropTypes.func.isRequired,
}

Select.defaultProps = {
  className: '',
  length: 'default',
  isDisabled: false,
  placeholder: '',
  options: [],
  defaultValue: null,
  value: null,
}

export default Select
