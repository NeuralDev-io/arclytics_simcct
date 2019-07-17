/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
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
import colours from '../../../styles/_colors_light.scss'

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
  } = props
  const classname = `${styles.select} ${length === 'default' ? '' : styles[length]} ${className || ''}`

  const customStyles = {
    container: provided => ({
      ...provided,
      width: (() => {
        if (length === 'short') return '6.5rem'
        if (length === 'long') return '10rem'
        if (length === 'stretch') return '100%'
        return '7.5rem'
      })(),
    }),
    control: (provided, state) => ({
      ...provided,
      backgroundColor: colours.n10,
      borderRadius: 6,
      borderColor: colours.n10,
      borderWidth: 1,
      padding: '0 .25rem 0 .55rem',
      height: '2.25rem',
      cursor: state.isDisabled ? 'not-allowed' : 'pointer',

      '&:hover': {
        backgroundColor: colours.n20,
        borderColor: colours.n20,
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
        if (state.isDisabled) return colours.n300
        if (state.hasValue) return colours.n900
        return colours.n600
      })(),
    }),
    option: provided => ({
      ...provided,
      padding: '.5rem .75rem',
    }),
    placeholder: (provided, state) => ({
      ...provided,
      color: state.isDisabled ? colours.n300 : colours.n600,
    }),
  }

  return (
    <ReactSelect
      className={classname}
      name={name}
      isClearable
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
          primary: colours.ag500,
          primary25: colours.ag50,
        },
      })}
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
