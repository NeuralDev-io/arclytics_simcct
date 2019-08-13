import React, { Component } from 'react'
import PropTypes from 'prop-types'
import CompForm from './CompForm'
import CompTable from './CompTable'
import Button from '../../elements/button'

import styles from './CompSidebar.module.scss'

// eslint-disable-next-line
class CompSidebar extends Component {
  render() {
    const {
      values,
      onChange,
      onSimulate,
      storeInit,
    } = this.props

    return (
      <div className={styles.sidebar}>
        <h4>Composition</h4>
        <CompForm
          values={values}
          onChange={onChange}
        />
        <CompTable
          data={values}
          onChange={onChange}
        />
        <Button
          onClick={onSimulate}
          length="long"
          className={styles.btn}
          isDisabled={!storeInit}
        >
          RUN
        </Button>
      </div>
    )
  }
}

CompSidebar.propTypes = {
  values: PropTypes.shape({
    alloyOption: PropTypes.string,
    parent: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    weld: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    mix: PropTypes.shape({
      name: PropTypes.string,
      compositions: PropTypes.arrayOf(PropTypes.shape({
        symbol: PropTypes.string,
        weight: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      })),
    }),
    dilution: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  onSimulate: PropTypes.func.isRequired,
  storeInit: PropTypes.bool.isRequired,
}

export default CompSidebar
